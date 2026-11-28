#!/usr/bin/env python3
"""
CMS-SUS-16-034  VZ electroweak signal region analysis
for TChiWZ_550_200 (m_chi+/chi20 = 550, m_chi10 = 200 GeV).

VZ region cuts (Table 1):
  - 2 OSSF leptons (ee/mumu), pT>25/20 GeV, |eta|<2.4, no ECAL gap
  - 86 < mll < 96 GeV, dilepton pT > 25 GeV
  - >= 2 jets pT>35 |eta|<2.4, 0 b-jets
  - No extra leptons (pT>10 veto)
  - MET > 100 GeV, min dphi(j1,j2 wrt MET) > 0.4
  - MT2(ll) > 80 GeV
  - mjj < 110 GeV (jet pair closest in dphi)
MET bins: [100-150, 150-250, 250-350, >350] GeV
"""
import os
import math
import yaml
import numpy as np
import uproot
import awkward as ak

LUMI_FB  = 35.9
MZ_LO    = 86.0
MZ_HI    = 96.0
MET_BINS = [100., 150., 250., 350., 450.]

# ── geometry helpers ──────────────────────────────────────────────────────────
def _dphi(a, b):
    d = a - b
    d = np.where(d >  math.pi, d - 2*math.pi, d)
    d = np.where(d < -math.pi, d + 2*math.pi, d)
    return np.abs(d)

def _dR(eta1, phi1, eta2, phi2):
    return np.sqrt((eta1-eta2)**2 + _dphi(phi1, phi2)**2)

def _invm(pt1, eta1, phi1, m1, pt2, eta2, phi2, m2):
    """Invariant mass of two 4-vectors (numpy, per-event)."""
    px1 = pt1*np.cos(phi1); py1 = pt1*np.sin(phi1); pz1 = pt1*np.sinh(eta1)
    E1  = np.sqrt(px1**2+py1**2+pz1**2+m1**2)
    px2 = pt2*np.cos(phi2); py2 = pt2*np.sin(phi2); pz2 = pt2*np.sinh(eta2)
    E2  = np.sqrt(px2**2+py2**2+pz2**2+m2**2)
    s = (E1+E2)**2 - (px1+px2)**2 - (py1+py2)**2 - (pz1+pz2)**2
    return np.sqrt(np.maximum(s, 0.))

def _mt2_ll_single(pt1, phi1, pt2, phi2, met_pt, met_phi):
    """
    MT2(ll) for one event using 200-point angular scan (massless invisibles).
    """
    met_x = met_pt * math.cos(met_phi)
    met_y = met_pt * math.sin(met_phi)
    best = math.inf
    for k in range(200):
        theta = -math.pi + 2*math.pi * k / 200
        # Scan q1 magnitude in steps of met_pt/100
        for step in range(101):
            q1 = met_pt * step / 100.
            q1x = q1 * math.cos(theta)
            q1y = q1 * math.sin(theta)
            q2x = met_x - q1x
            q2y = met_y - q1y
            # mT^2 for each lepton
            cos1 = math.cos(math.atan2(q1y, q1x) - phi1) if q1 > 0 else -1.
            cos2 = math.cos(math.atan2(q2y, q2x) - phi2) if (q2x**2+q2y**2) > 0 else -1.
            q2 = math.sqrt(q2x**2+q2y**2)
            mt1_sq = 2*pt1*q1*(1-cos1) if q1>0 else 0.
            mt2_sq = 2*pt2*q2*(1-cos2) if q2>0 else 0.
            val = max(mt1_sq, mt2_sq)
            if val < best:
                best = val
    return math.sqrt(best)

# ── analysis ──────────────────────────────────────────────────────────────────
def run_analysis(root_path, xsec_pb, n_gen):
    """Return 4-bin MET histogram (counts × weight_per_event) for one ROOT file."""
    weight = xsec_pb * 1000. * LUMI_FB / n_gen  # pb->fb, then ×lumi/n_gen
    f    = uproot.open(root_path)
    tree = f["Delphes"]
    n_ev = tree.num_entries

    # ── load branches ──────────────────────────────────────────────────────
    el_pt  = tree["Electron/Electron.PT"].array()
    el_eta = tree["Electron/Electron.Eta"].array()
    el_phi = tree["Electron/Electron.Phi"].array()
    el_ch  = tree["Electron/Electron.Charge"].array()

    mu_pt  = tree["Muon/Muon.PT"].array()
    mu_eta = tree["Muon/Muon.Eta"].array()
    mu_phi = tree["Muon/Muon.Phi"].array()
    mu_ch  = tree["Muon/Muon.Charge"].array()

    jt_pt   = tree["Jet/Jet.PT"].array()
    jt_eta  = tree["Jet/Jet.Eta"].array()
    jt_phi  = tree["Jet/Jet.Phi"].array()
    jt_mass = tree["Jet/Jet.Mass"].array()
    jt_btag = tree["Jet/Jet.BTag"].array()

    met_v  = tree["MissingET/MissingET.MET"].array()
    mphi_v = tree["MissingET/MissingET.Phi"].array()

    # ── per-event MET ──────────────────────────────────────────────────────
    met     = ak.firsts(met_v,  axis=1)   # shape (n_ev,)
    met_phi = ak.firsts(mphi_v, axis=1)
    ev_mask = (~ak.is_none(met)) & (met > 100.)

    # ── apply base lepton quality cuts ────────────────────────────────────
    # electrons: pT>10, |eta|<2.4, not in ECAL gap [1.4,1.6]
    e_ok = ((el_pt > 10.) & (np.abs(el_eta) < 2.4) &
            ~((np.abs(el_eta) > 1.4) & (np.abs(el_eta) < 1.6)))
    el_pt_s  = el_pt[e_ok];  el_eta_s = el_eta[e_ok]
    el_phi_s = el_phi[e_ok]; el_ch_s  = el_ch[e_ok]

    # muons: pT>10, |eta|<2.4
    m_ok = (mu_pt > 10.) & (np.abs(mu_eta) < 2.4)
    mu_pt_s  = mu_pt[m_ok];  mu_eta_s = mu_eta[m_ok]
    mu_phi_s = mu_phi[m_ok]; mu_ch_s  = mu_ch[m_ok]

    # total lepton count per event
    n_lep = ak.num(el_pt_s) + ak.num(mu_pt_s)

    # ── find exactly 2 leptons (handles extra-lepton veto) ───────────────
    ev_mask = ev_mask & (n_lep == 2)

    # ── OSSF pair selection ───────────────────────────────────────────────
    # Case A: 2 electrons
    ee_mask = (ak.num(el_pt_s) == 2) & (ak.num(mu_pt_s) == 0)
    # Case B: 2 muons
    mm_mask = (ak.num(mu_pt_s) == 2) & (ak.num(el_pt_s) == 0)

    ev_mask = ev_mask & (ee_mask | mm_mask)

    # ── lepton kinematics ─────────────────────────────────────────────────
    # For electrons
    ee_ev = ev_mask & ee_mask
    mm_ev = ev_mask & mm_mask

    # Electron pair properties (only where ee_ev is True)
    el_pt1  = ak.firsts(el_pt_s);   el_pt2  = ak.pad_none(el_pt_s,  2)[:, 1]
    el_eta1 = ak.firsts(el_eta_s);  el_eta2 = ak.pad_none(el_eta_s, 2)[:, 1]
    el_phi1 = ak.firsts(el_phi_s);  el_phi2 = ak.pad_none(el_phi_s, 2)[:, 1]
    el_ch1  = ak.firsts(el_ch_s);   el_ch2  = ak.pad_none(el_ch_s,  2)[:, 1]

    # Muon pair properties
    mu_pt1  = ak.firsts(mu_pt_s);   mu_pt2  = ak.pad_none(mu_pt_s,  2)[:, 1]
    mu_eta1 = ak.firsts(mu_eta_s);  mu_eta2 = ak.pad_none(mu_eta_s, 2)[:, 1]
    mu_phi1 = ak.firsts(mu_phi_s);  mu_phi2 = ak.pad_none(mu_phi_s, 2)[:, 1]
    mu_ch1  = ak.firsts(mu_ch_s);   mu_ch2  = ak.pad_none(mu_ch_s,  2)[:, 1]

    def _safe(arr, default=0.):
        return ak.to_numpy(ak.fill_none(arr, default))

    el_pt1_np  = _safe(el_pt1);   el_pt2_np  = _safe(el_pt2)
    el_eta1_np = _safe(el_eta1);  el_eta2_np = _safe(el_eta2)
    el_phi1_np = _safe(el_phi1);  el_phi2_np = _safe(el_phi2)
    el_ch1_np  = _safe(el_ch1,0); el_ch2_np  = _safe(el_ch2,0)

    mu_pt1_np  = _safe(mu_pt1);   mu_pt2_np  = _safe(mu_pt2)
    mu_eta1_np = _safe(mu_eta1);  mu_eta2_np = _safe(mu_eta2)
    mu_phi1_np = _safe(mu_phi1);  mu_phi2_np = _safe(mu_phi2)
    mu_ch1_np  = _safe(mu_ch1,0); mu_ch2_np  = _safe(mu_ch2,0)

    ee_np = ak.to_numpy(ee_ev)
    mm_np = ak.to_numpy(mm_ev)
    ev_np = ak.to_numpy(ev_mask)

    # leading pT
    ee_lead_ok = np.where(ee_np,
                          (np.maximum(el_pt1_np, el_pt2_np) > 25.) &
                          (np.minimum(el_pt1_np, el_pt2_np) > 20.), False)
    mm_lead_ok = np.where(mm_np,
                          (np.maximum(mu_pt1_np, mu_pt2_np) > 25.) &
                          (np.minimum(mu_pt1_np, mu_pt2_np) > 20.), False)
    ev_np = ev_np & (ee_lead_ok | mm_lead_ok)

    # Opposite sign
    ee_os = (el_ch1_np + el_ch2_np == 0)
    mm_os = (mu_ch1_np + mu_ch2_np == 0)
    ev_np = ev_np & np.where(ee_np, ee_os, np.where(mm_np, mm_os, False))

    # dR > 0.1
    ee_dr = np.where(ee_np, _dR(el_eta1_np, el_phi1_np, el_eta2_np, el_phi2_np), 1.)
    mm_dr = np.where(mm_np, _dR(mu_eta1_np, mu_phi1_np, mu_eta2_np, mu_phi2_np), 1.)
    ev_np = ev_np & (np.where(ee_np, ee_dr, mm_dr) > 0.1)

    # Lepton 4-vectors (use electrons if ee_ev, muons if mm_ev)
    lm = 0.000511  # electron mass
    mm_mass = 0.10566  # muon mass
    l1_pt  = np.where(ee_np, el_pt1_np,  mu_pt1_np)
    l2_pt  = np.where(ee_np, el_pt2_np,  mu_pt2_np)
    l1_eta = np.where(ee_np, el_eta1_np, mu_eta1_np)
    l2_eta = np.where(ee_np, el_eta2_np, mu_eta2_np)
    l1_phi = np.where(ee_np, el_phi1_np, mu_phi1_np)
    l2_phi = np.where(ee_np, el_phi2_np, mu_phi2_np)
    l_m    = np.where(ee_np, lm, mm_mass)

    # Sort so l1 is leading
    swap = l2_pt > l1_pt
    l1_pt_s  = np.where(swap, l2_pt,  l1_pt);   l2_pt_s  = np.where(swap, l1_pt,  l2_pt)
    l1_eta_s = np.where(swap, l2_eta, l1_eta);  l2_eta_s = np.where(swap, l1_eta, l2_eta)
    l1_phi_s = np.where(swap, l2_phi, l1_phi);  l2_phi_s = np.where(swap, l1_phi, l2_phi)

    # mll
    mll = _invm(l1_pt_s, l1_eta_s, l1_phi_s, l_m,
                l2_pt_s, l2_eta_s, l2_phi_s, l_m)
    ev_np = ev_np & (mll > MZ_LO) & (mll < MZ_HI)

    # Dilepton pT > 25
    pxll = l1_pt_s*np.cos(l1_phi_s) + l2_pt_s*np.cos(l2_phi_s)
    pyll = l1_pt_s*np.sin(l1_phi_s) + l2_pt_s*np.sin(l2_phi_s)
    ptll = np.sqrt(pxll**2 + pyll**2)
    ev_np = ev_np & (ptll > 25.)

    # ── jet selection ─────────────────────────────────────────────────────
    # Jets pT>35, |eta|<2.4, cleaned against leptons
    j_base = (jt_pt > 35.) & (np.abs(jt_eta) < 2.4)
    # Clean against l1 and l2
    dR_jl1 = _dR(jt_eta, jt_phi,
                  ak.broadcast_arrays(jt_eta, l1_eta_s)[1],  # broadcast scalar
                  ak.broadcast_arrays(jt_phi, l1_phi_s)[1])
    dR_jl2 = _dR(jt_eta, jt_phi,
                  ak.broadcast_arrays(jt_eta, l2_eta_s)[1],
                  ak.broadcast_arrays(jt_phi, l2_phi_s)[1])
    j_clean = j_base & (dR_jl1 > 0.4) & (dR_jl2 > 0.4)

    good_jets_pt   = jt_pt[j_clean]
    good_jets_eta  = jt_eta[j_clean]
    good_jets_phi  = jt_phi[j_clean]
    good_jets_mass = jt_mass[j_clean]
    good_jets_btag = jt_btag[j_clean]

    n_jets  = ak.num(good_jets_pt)
    n_bjets = ak.sum(good_jets_btag > 0, axis=1)

    ev_np = ev_np & (ak.to_numpy(n_jets) >= 2) & (ak.to_numpy(n_bjets) == 0)

    # ── dphi(leading jets, MET) > 0.4 ────────────────────────────────────
    met_np    = ak.to_numpy(ak.fill_none(met, 0.))
    met_phi_np = ak.to_numpy(ak.fill_none(met_phi, 0.))

    j1_phi = ak.to_numpy(ak.fill_none(ak.firsts(good_jets_phi),                        0.))
    j2_phi = ak.to_numpy(ak.fill_none(ak.firsts(good_jets_phi[:, 1:]),                 0.))

    dphi_j1_met = _dphi(j1_phi, met_phi_np)
    dphi_j2_met = _dphi(j2_phi, met_phi_np)
    ev_np = ev_np & (dphi_j1_met > 0.4) & (dphi_j2_met > 0.4)

    # ── mjj < 110 GeV (jet pair closest in dphi) ─────────────────────────
    # Compute mjj for all jet pairs per event; keep the pair with smallest dphi
    # We vectorise by considering all pairs from ak.combinations
    jet_pairs = ak.combinations(
        ak.zip({"pt": good_jets_pt, "eta": good_jets_eta,
                "phi": good_jets_phi, "m": good_jets_mass}),
        2, fields=["j1", "j2"]
    )
    # dphi of each pair
    pair_dphi = _dphi(jet_pairs["j1"]["phi"], jet_pairs["j2"]["phi"])
    # invariant mass of each pair
    pair_mjj  = _invm(jet_pairs["j1"]["pt"], jet_pairs["j1"]["eta"],
                      jet_pairs["j1"]["phi"], jet_pairs["j1"]["m"],
                      jet_pairs["j2"]["pt"], jet_pairs["j2"]["eta"],
                      jet_pairs["j2"]["phi"], jet_pairs["j2"]["m"])
    # pick pair with smallest dphi (or return inf if no pairs)
    idx_min  = ak.argmin(pair_dphi, axis=1, keepdims=True)
    mjj_min_dphi = ak.firsts(pair_mjj[idx_min])
    mjj_np = ak.to_numpy(ak.fill_none(mjj_min_dphi, 999.))
    ev_np  = ev_np & (mjj_np < 110.)

    # ── MT2(ll) > 80 GeV — computed only for pre-selected events ─────────
    # (uses a small Python loop, but only over passing events — not range(n_events))
    passing_indices = np.where(ev_np)[0]
    print(f"  Events before MT2: {len(passing_indices)}", flush=True)

    hist = np.zeros(4)
    for idx in passing_indices:
        mt2 = _mt2_ll_single(
            float(l1_pt_s[idx]),  float(l1_phi_s[idx]),
            float(l2_pt_s[idx]),  float(l2_phi_s[idx]),
            float(met_np[idx]),   float(met_phi_np[idx])
        )
        if mt2 < 80.:
            continue
        this_met = float(met_np[idx])
        ibin = int(np.searchsorted(MET_BINS[1:], this_met))
        ibin = min(ibin, 3)
        hist[ibin] += weight

    print(f"  Events passing VZ: {int(np.sum(hist)/weight)}", flush=True)
    return hist


def main():
    # ── load metadata ──────────────────────────────────────────────────────
    with open("datasets.yaml") as f:
        datasets = yaml.safe_load(f) or []

    # ── cross section and event count ─────────────────────────────────────
    with open("data/xsec_pb.txt") as f:
        xsec_pb = float(f.read().strip())
    with open("data/n_generated.txt") as f:
        n_gen = int(f.read().strip())

    print(f"Cross section: {xsec_pb:.6e} pb,  N_gen: {n_gen}", flush=True)

    total_hist = np.zeros(4)
    for ds in datasets:
        if ds.get("status", "").startswith("BLOCKED"):
            continue
        for url in ds.get("file_urls", []):
            print(f"\nProcessing {url}", flush=True)
            total_hist += run_analysis(url, xsec_pb, n_gen)

    print("\nVZ MET histogram:", flush=True)
    for i, (lo, hi) in enumerate(zip(MET_BINS[:-1], MET_BINS[1:])):
        print(f"  [{lo:.0f}, {hi:.0f}]: {total_hist[i]:.4f} events @ {LUMI_FB} fb-1")

    # ── update results YAML ───────────────────────────────────────────────
    yaml_path = "results/histogram_TChiWZ.yaml"
    with open(yaml_path) as f:
        raw = f.read()
    docs = list(yaml.safe_load_all(raw))
    meta, histo = docs[0], docs[1]
    for i in range(4):
        histo["dependent_variables"][0]["values"][i]["value"] = round(float(total_hist[i]), 6)
    with open(yaml_path, "w") as f:
        yaml.dump(meta, f, default_flow_style=False, sort_keys=False)
        f.write("---\n")
        yaml.dump(histo, f, default_flow_style=False, sort_keys=False)
    print(f"\nResults written to {yaml_path}", flush=True)


if __name__ == "__main__":
    main()
