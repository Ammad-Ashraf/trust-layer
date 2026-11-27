"""
CMS-SUS-16-046 T5Wg analysis — vectorized with awkward-array.
Reads inputs from datasets.yaml and fills results/*.yaml.

Signal region (Table 1):
  >= 1 photon pT>180 GeV, |eta|<1.44, dR(gamma,jet)>0.5
  dphi(MET, jet)>0.3 for jets pT>100 GeV
  MET>300 GeV, MT(gamma,MET)>300 GeV, S_T^gamma>600 GeV
"""
import argparse
import numpy as np
import awkward as ak
import uproot
import yaml
import os

BIN_EDGES = np.array([600.0, 800.0, 1000.0, 1300.0])
TRIGGER_EFF = 0.943  # CMS-SUS-16-046 Sec. 5


def _dphi(a, b):
    return np.arctan2(np.sin(a - b), np.cos(a - b))


def analyze(input_root, xsec_fb, lumi_fb, n_gen):
    f = uproot.open(input_root)
    tree = f["Delphes"]
    n_events = tree.num_entries

    def load(a, b):
        try:
            return tree[a].array()
        except Exception:
            return tree[b].array()

    pho_pt      = load("Photon/Photon.PT",        "Photon.PT")
    pho_eta     = load("Photon/Photon.Eta",       "Photon.Eta")
    pho_phi     = load("Photon/Photon.Phi",       "Photon.Phi")
    jet_pt      = load("Jet/Jet.PT",              "Jet.PT")
    jet_eta     = load("Jet/Jet.Eta",             "Jet.Eta")
    jet_phi     = load("Jet/Jet.Phi",             "Jet.Phi")
    met_all     = load("MissingET/MissingET.MET", "MissingET.MET")
    met_phi_all = load("MissingET/MissingET.Phi", "MissingET.Phi")

    met     = met_all[:, 0]
    met_phi = met_phi_all[:, 0]

    pho = ak.zip({"pt": pho_pt, "eta": pho_eta, "phi": pho_phi})
    jet = ak.zip({"pt": jet_pt, "eta": jet_eta, "phi": jet_phi})

    # 1. Basic photon selection: pT>180 GeV, |eta|<1.44 (ECAL barrel)
    pho = pho[(pho.pt > 180.0) & (np.abs(pho.eta) < 1.44)]

    # 2. Jet selection: pT>30 GeV, |eta|<3.0
    jet = jet[(jet.pt > 30.0) & (np.abs(jet.eta) < 3.0)]

    # 3. dR(photon, nearest jet) > 0.5
    #    ak.cartesian nested=True → (n_events, n_pho, n_jet), reduce over jets
    pho_jet = ak.cartesian({"p": pho, "j": jet}, nested=True)
    dr2 = (_dphi(pho_jet["p"].phi, pho_jet["j"].phi) ** 2
           + (pho_jet["p"].eta - pho_jet["j"].eta) ** 2)
    min_dr2 = ak.fill_none(ak.min(dr2, axis=-1), 9999.0)
    pho = pho[min_dr2 > 0.25]

    has_pho = ak.num(pho) >= 1

    # 4. dphi(MET, hard jet) > 0.3  (jets with pT>100 GeV)
    hard = jet[jet.pt > 100.0]
    met_phi_sg = ak.Array([[x] for x in ak.to_list(met_phi)])  # (n_events, 1)
    mj = ak.cartesian({"m": met_phi_sg, "j": hard.phi})
    dphi_mj   = np.abs(_dphi(mj["m"], mj["j"]))
    min_dphi  = ak.fill_none(ak.min(dphi_mj, axis=-1), 9999.0)
    pass_dphi = min_dphi > 0.3

    # 5. MET > 300 GeV
    pass_met = met > 300.0

    # 6. MT(leading photon, MET) > 300 GeV
    lead_pt  = ak.firsts(pho.pt)
    lead_phi = ak.firsts(pho.phi)
    dp_gmet  = np.abs(_dphi(lead_phi, met_phi))
    mt       = np.sqrt(2.0 * lead_pt * met * (1.0 - np.cos(dp_gmet)))
    pass_mt  = ak.fill_none(mt > 300.0, False)

    # 7. S_T^gamma = MET + sum(pT of all selected photons) > 600 GeV
    st      = met + ak.sum(pho.pt, axis=-1)
    pass_st = st > 600.0

    sel      = has_pho & pass_dphi & pass_met & pass_mt & pass_st
    n_signal = int(ak.sum(sel))
    weight   = (xsec_fb * lumi_fb) / n_gen

    # Bin S_T^gamma using digitize (vectorized, no event loop)
    st_sel    = ak.to_numpy(st[sel])
    bin_idx   = np.clip(np.digitize(st_sel, BIN_EDGES) - 1, 0, 3)
    raw_cts   = np.bincount(bin_idx, minlength=4)
    bin_counts = raw_cts.astype(float) * weight * TRIGGER_EFF

    # Cutflow
    n_pho  = int(ak.sum(has_pho))
    n_dphi = int(ak.sum(has_pho & pass_dphi))
    n_met  = int(ak.sum(has_pho & pass_dphi & pass_met))
    n_mt   = int(ak.sum(has_pho & pass_dphi & pass_met & pass_mt))
    eff    = n_signal / n_gen

    print(f"Loaded {n_events} events from {input_root}")
    print(f"Weight/event = {xsec_fb:.4f} fb * {lumi_fb:.1f} fb^-1 / {n_gen} = {weight:.6f}")
    print(f"\nCutflow:")
    print(f"  In Delphes:          {n_events}")
    print(f"  >= 1 barrel photon:  {n_pho}")
    print(f"  dphi(MET,jet)>0.3:   {n_dphi}")
    print(f"  MET > 300 GeV:       {n_met}")
    print(f"  MT > 300 GeV:        {n_mt}")
    print(f"  S_T^g > 600 GeV:     {n_signal}")
    print(f"  Efficiency (N/N_gen): {eff:.5f}")
    print(f"\nS_T^gamma signal yields (L={lumi_fb} fb^-1, NLO xsec={xsec_fb} fb):")
    for k in range(4):
        lo = int(BIN_EDGES[k])
        hi = int(BIN_EDGES[k + 1]) if k < 3 else "inf"
        print(f"  [{lo},{hi}) GeV: {bin_counts[k]:.4f}")
    print(f"  Total: {np.sum(bin_counts):.4f}")

    return bin_counts, n_signal, n_events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",   default=None)
    parser.add_argument("--xsec",    type=float, default=2.5)
    parser.add_argument("--lumi",    type=float, default=35.9)
    parser.add_argument("--nevents", type=int,   default=50000)
    args = parser.parse_args()

    if args.input is None:
        with open("datasets.yaml") as fh:
            datasets = yaml.safe_load(fh)
        args.input = datasets[0]["file_urls"][0]

    print(f"CMS-SUS-16-046 T5Wg | xsec={args.xsec} fb | L={args.lumi} fb^-1 | N={args.nevents}")
    bin_counts, n_signal, n_events = analyze(args.input, args.xsec, args.lumi, args.nevents)

    ws = os.path.dirname(os.path.abspath(__file__))
    for fn in sorted(os.listdir(os.path.join(ws, "results"))):
        if fn.endswith(".yaml"):
            results_yaml = os.path.join(ws, "results", fn)
            break

    with open(results_yaml) as fh:
        content = fh.read()
    parts = content.split("---\n", 1)
    meta = parts[0] if len(parts) == 2 else ""
    data = yaml.safe_load(parts[1] if len(parts) == 2 else content)
    for k, v in enumerate(data["dependent_variables"][0]["values"]):
        v["value"] = round(float(bin_counts[k]), 6)
    with open(results_yaml, "w") as fh:
        fh.write(meta)
        fh.write("---\n")
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False)
    print(f"Written to {results_yaml}")


if __name__ == "__main__":
    main()
