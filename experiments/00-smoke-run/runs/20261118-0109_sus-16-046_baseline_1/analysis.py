"""
CMS-SUS-16-046 event selection for T5Wg_1750_1700 signal.

Implements the analysis in Table 1 of the paper:
  Preselection: >=1 photon pT>180 GeV |eta|<1.44, DR(gamma,jet)>0.5,
                Dphi(MET,jet)>0.3 for jets pT>100 GeV
  Signal region: pT_miss>300, MT(gamma,MET)>300, S_T^gamma>600 GeV

S_T^gamma = pT_miss + sum_i pT(gamma_i) [all reconstructed photons]
Bins: [600,800), [800,1000), [1000,1300), [1300,inf) GeV
"""
import os
import numpy as np
import uproot
import awkward as ak
import yaml

# ─── Configuration ────────────────────────────────────────────────────────────
WS = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(WS) == 'analysis':
    WS = os.path.dirname(WS)

DATASETS_YAML = os.path.join(WS, 'datasets.yaml')
PHOTON_EFF_FILE = os.path.join(WS, 'object_efficiencies', 'photon_eff_LoosePixelVeto.root')
YAML_FILE = os.path.join(WS, 'results', 'histogram_T5Wg.yaml')

# NLO cross section from Prospino (pb) and luminosity
XSEC_NLO_FB  = 3.96      # fb — NLO from Prospino for m_g=1750 GeV, 13 TeV
LUMI_FB      = 35.9       # fb^-1
N_GEN        = 10000      # generated events

# Corrections
TRIG_EFF               = 0.943  # trigger efficiency (paper Section 5)
DELPHES_PHOTON_EFF     = 0.95   # barrel photon efficiency in delphes_card_CMS.tcl
# CMS barrel photon efficiency from photon_eff_LoosePixelVeto.root
# (|eta|<0.8, ET>90 GeV): 0.848; (0.8<|eta|<1.44, ET>90 GeV): 0.809
CMS_PHOTON_EFF_LOW  = 0.84810555
CMS_PHOTON_EFF_HIGH = 0.80869347

# ─── Load file path from datasets.yaml ───────────────────────────────────────
with open(DATASETS_YAML) as _f:
    _datasets = yaml.safe_load(_f)
ROOT_FILE = os.path.join(WS, _datasets[0]['file_urls'][0])
print(f"Input: {ROOT_FILE}")


def dphi(phi1, phi2):
    """Signed angular difference phi1 - phi2, folded to [-pi, pi]."""
    d = phi1 - phi2
    d = np.where(d > np.pi, d - 2*np.pi, d)
    d = np.where(d < -np.pi, d + 2*np.pi, d)
    return d


def run_analysis():
    f = uproot.open(ROOT_FILE)
    tree = f['Delphes']
    print(f"Events: {tree.num_entries}")

    # ── Read all needed branches ──────────────────────────────────────────
    photon_pt  = tree["Photon/Photon.PT"].array()
    photon_eta = tree["Photon/Photon.Eta"].array()
    photon_phi = tree["Photon/Photon.Phi"].array()
    jet_pt     = tree["Jet/Jet.PT"].array()
    jet_eta    = tree["Jet/Jet.Eta"].array()
    jet_phi    = tree["Jet/Jet.Phi"].array()
    met        = ak.flatten(tree["MissingET/MissingET.MET"].array()).to_numpy()
    met_phi    = ak.flatten(tree["MissingET/MissingET.Phi"].array()).to_numpy()

    n = len(met)

    # ── Identify barrel photons (pT>180, |eta|<1.44) ─────────────────────
    barrel = (photon_pt > 180) & (np.abs(photon_eta) < 1.44)
    has_barrel = ak.any(barrel, axis=1).to_numpy()

    # Leading barrel photon pT/eta/phi
    # Zero-pad with large-negative eta to signal "no photon"
    lead_pt_jag  = ak.where(barrel, photon_pt, 0)
    lead_eta_jag = ak.where(barrel, photon_eta, 0.0)
    lead_phi_jag = ak.where(barrel, photon_phi, 0.0)

    lead_idx = ak.argmax(lead_pt_jag, axis=1, keepdims=True)
    lead_pt_ak  = ak.flatten(photon_pt[lead_idx])
    lead_eta_ak = ak.flatten(photon_eta[lead_idx])
    lead_phi_ak = ak.flatten(photon_phi[lead_idx])
    lead_pt  = ak.to_numpy(lead_pt_ak)
    lead_eta = ak.to_numpy(lead_eta_ak)
    lead_phi = ak.to_numpy(lead_phi_ak)
    # Zero out entries where there is no barrel photon
    lead_pt  = np.where(has_barrel, lead_pt, 0.0)
    lead_eta = np.where(has_barrel, lead_eta, 0.0)
    lead_phi = np.where(has_barrel, lead_phi, 0.0)

    # ── ΔR(leading photon, jets) > 0.5 ───────────────────────────────────
    # Compute DR of each jet with the leading barrel photon (broadcast)
    # lead_eta/phi: (n,) → broadcast with jet_eta/phi: (n, nj)
    lead_eta_bc = ak.broadcast_arrays(lead_eta, jet_eta)[0]
    lead_phi_bc = ak.broadcast_arrays(lead_phi, jet_phi)[0]
    dr_jet = np.sqrt((jet_eta - lead_eta_bc)**2 +
                     dphi(jet_phi, lead_phi_bc)**2)
    # Photon isolated if ALL jets have DR > 0.5
    photon_jet_ok = ak.all(dr_jet > 0.5, axis=1).to_numpy()
    # For events without barrel photon, don't apply this cut
    photon_jet_ok = np.where(has_barrel, photon_jet_ok, True)

    # ── Δφ(MET, jet) > 0.3 for jets with pT > 100 GeV ───────────────────
    high_pt_jets = jet_pt > 100
    jet_phi_high = ak.where(high_pt_jets, jet_phi, 999.0)  # 999=no jet sentinel
    met_phi_bc   = ak.broadcast_arrays(met_phi, jet_phi_high)[0]
    dphi_met_jet = np.abs(dphi(jet_phi_high, met_phi_bc))
    # Where there are high-pT jets (sentinel 999 gives large dphi), all must pass
    has_high_pt_jet = ak.any(high_pt_jets, axis=1).to_numpy()
    met_dphi_ok = ak.all(
        (jet_phi_high > 900) | (dphi_met_jet > 0.3),
        axis=1
    ).to_numpy()
    met_dphi_ok = np.where(has_high_pt_jet, met_dphi_ok, True)

    # ── Preselection ──────────────────────────────────────────────────────
    presel = has_barrel & photon_jet_ok & met_dphi_ok
    print(f"Preselection: {presel.sum()} / {n}")

    # ── MT(gamma_lead, MET) ───────────────────────────────────────────────
    dphi_gmet = np.abs(dphi(lead_phi, met_phi))
    MT = np.sqrt(2.0 * lead_pt * met * (1.0 - np.cos(dphi_gmet)))

    # ── S_T^gamma = MET + sum of ALL photon pT ────────────────────────────
    all_photon_pt_sum = ak.sum(photon_pt, axis=1).to_numpy()
    ST = met + all_photon_pt_sum

    # ── Signal region ─────────────────────────────────────────────────────
    sr = presel & (met > 300) & (MT > 300) & (ST > 600)
    print(f"Signal region: {sr.sum()}")

    # ── S_T^gamma binning ─────────────────────────────────────────────────
    ST_sr    = ST[sr]
    eta_sr   = lead_eta[sr]
    pt_sr    = lead_pt[sr]

    bin_edges = [600, 800, 1000, 1300, np.inf]
    raw = np.array([
        np.sum((ST_sr >= lo) & (ST_sr < hi))
        for lo, hi in zip(bin_edges[:-1], bin_edges[1:])
    ])
    print(f"\nRaw S_T^gamma bins: {raw.tolist()}")

    # ── Weights ───────────────────────────────────────────────────────────
    w_base = XSEC_NLO_FB * LUMI_FB / N_GEN  # = 3.96 * 35.9 / 10000 = 0.01421

    # Per-event photon efficiency scale factor (CMS / Delphes)
    abs_eta_sr = np.abs(eta_sr)
    cms_eff = np.where(abs_eta_sr < 0.8, CMS_PHOTON_EFF_LOW, CMS_PHOTON_EFF_HIGH)
    phot_sf = cms_eff / DELPHES_PHOTON_EFF

    # Bin yields = sum of weighted events in each bin
    bin_yields = np.array([
        np.sum(
            phot_sf[(ST_sr >= lo) & (ST_sr < hi)]
        ) * w_base * TRIG_EFF
        for lo, hi in zip(bin_edges[:-1], bin_edges[1:])
    ])

    print(f"\nExpected yields at {LUMI_FB} fb^-1 (NLO xsec = {XSEC_NLO_FB} fb):")
    names = ["[600,800)", "[800,1000)", "[1000,1300)", "[1300,inf)"]
    for name, raw_i, yld in zip(names, raw, bin_yields):
        print(f"  S_T^gamma {name}: {raw_i} MC events -> {yld:.4f} expected")
    print(f"  Total: {bin_yields.sum():.4f}")

    # ── Write YAML ────────────────────────────────────────────────────────
    with open(YAML_FILE) as fh:
        full_text = fh.read()
    parts = full_text.split('---')
    meta_text = parts[0]
    hist_data = yaml.safe_load(parts[1])

    for b in range(4):
        hist_data['dependent_variables'][0]['values'][b]['value'] = round(float(bin_yields[b]), 6)

    with open(YAML_FILE, 'w') as fh:
        fh.write(meta_text)
        fh.write('---\n')
        yaml.dump(hist_data, fh, default_flow_style=False, allow_unicode=True)

    print(f"\nResults written to {YAML_FILE}")
    return bin_yields


if __name__ == '__main__':
    run_analysis()
