"""Grafik Plotly yang dipakai di beberapa halaman."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from .model import Konfigurasi, probabilitas
from .ui import STATUS_WARNA, WARNA

_FONT = dict(family="Plus Jakarta Sans, Segoe UI, sans-serif", size=12)


def _rapi(fig: go.Figure, tinggi: int = 320) -> go.Figure:
    fig.update_layout(height=tinggi, margin=dict(l=10, r=10, t=30, b=10), font=_FONT,
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                      separators=",.", hoverlabel=dict(font=_FONT))
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    return fig


def tren(df: pd.DataFrame, definisi: str = "d2") -> go.Figure:
    fig = go.Figure()
    for col, nama, warna in [(f"{definisi}_jiwa", "Jiwa", WARNA["utama"]), (f"{definisi}_umum", "Umum", WARNA["kedua"])]:
        fig.add_trace(go.Scatter(x=df["tahun"], y=df[col], name=nama, mode="lines+markers",
                                 line=dict(color=warna, width=2), marker=dict(size=6),
                                 hovertemplate="%{x}: %{y:.1f}%<extra>" + nama + "</extra>"))
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_xaxes(dtick=1)
    return _rapi(fig)


def auc_bar(df: pd.DataFrame) -> go.Figure:
    d = df.sort_values("auc_d2")
    warna = [WARNA["utama"] if v >= 0.6 else WARNA["redup"] for v in d["auc_d2"]]
    fig = go.Figure(go.Bar(x=d["auc_d2"] - 0.5, base=0.5, y=d["indikator"], orientation="h", marker_color=warna,
                           text=[f"{v:.3f}".replace(".", ",") for v in d["auc_d2"]], textposition="outside",
                           customdata=d["auc_d2"], hovertemplate="%{y}<br>AUC %{customdata:.3f}<extra></extra>"))
    fig.add_vline(x=0.5, line_dash="dash", line_color=WARNA["kritis"], annotation_text="acak (0,5)",
                  annotation_position="top")
    fig.update_xaxes(range=[0.4, 0.8])
    return _rapi(fig, 420)


def oos(df: pd.DataFrame) -> go.Figure:
    d = df.iloc[::-1]
    utama = d["model"].str.startswith("B2 EWS")
    fig = go.Figure(go.Scatter(
        x=d["auc"], y=d["model"], mode="markers",
        marker=dict(size=np.where(utama, 12, 9), color=np.where(utama, WARNA["utama"], WARNA["redup"])),
        error_x=dict(type="data", symmetric=False, array=d["auc_hi"] - d["auc"], arrayminus=d["auc"] - d["auc_lo"],
                     color="rgba(90,100,110,0.6)", thickness=2, width=0),
        customdata=np.stack([d["auc_lo"], d["auc_hi"], d["brier"]], axis=1),
        hovertemplate="%{y}<br>AUC %{x:.3f} (%{customdata[0]:.3f}–%{customdata[1]:.3f})"
                      "<br>Brier %{customdata[2]:.3f}<extra></extra>"))
    fig.update_xaxes(range=[0.5, 0.9], title="AUC out-of-sample (IK 95%)")
    return _rapi(fig, 380)


def profil(df: pd.DataFrame, kolom: str, judul: str, ambang: float | None = None) -> go.Figure:
    merah = (df[kolom] < 0) | ((ambang is not None) & (df[kolom] > (ambang or 0)))
    fig = go.Figure(go.Scatter(x=df["k"], y=df[kolom], mode="lines+markers+text",
                               line=dict(color=WARNA["utama"], width=2),
                               marker=dict(size=9, color=np.where(merah, WARNA["kritis"], WARNA["utama"])),
                               text=[f"{v:.1f}".replace(".", ",") for v in df[kolom]], textposition="top center",
                               customdata=df["n_kasus"],
                               hovertemplate="k = %{x}<br>Median %{y:.1f}%<br>n = %{customdata}<extra></extra>"))
    fig.add_hline(y=0, line_color="rgba(90,100,110,0.6)")
    if ambang is not None:
        fig.add_hline(y=ambang, line_dash="dash", line_color=WARNA["kritis"])
    fig.update_xaxes(tickvals=list(df["k"]), ticktext=[f"k={k}" for k in df["k"]])
    fig.update_layout(title=dict(text=judul, font=dict(size=13)))
    return _rapi(fig, 260)


def distribusi(df: pd.DataFrame) -> go.Figure:
    d = df.sort_values("urut")
    warna_jiwa = [WARNA["kritis"] if a else WARNA["utama"] for a in d["alarm"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d["kelompok"], y=d["umum"], name="Umum", marker_color=WARNA["redup"]))
    fig.add_trace(go.Bar(x=d["kelompok"], y=d["jiwa"], name="Jiwa (merah = alarm)", marker_color=warna_jiwa))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title="Jumlah perusahaan")
    return _rapi(fig)


def sensitivitas(x: dict, cfg: Konfigurasi, ambang: float) -> go.Figure:
    rk = np.arange(0, 201, 2)
    base = pd.DataFrame([x] * len(rk))
    base["rasio_klaim"] = rk
    p = probabilitas(base, cfg)
    p_now = float(probabilitas(pd.DataFrame([x]), cfg)[0])
    fig = go.Figure(go.Scatter(x=rk, y=p * 100, mode="lines", line=dict(color=WARNA["utama"], width=2),
                               fill="tozeroy", fillcolor="rgba(31,111,178,0.12)",
                               hovertemplate="Rasio klaim %{x}%<br>Probabilitas %{y:.1f}%<extra></extra>", name=""))
    fig.add_hline(y=ambang * 100, line_dash="dash", line_color=WARNA["kritis"],
                  annotation_text=f"ambang {ambang * 100:.1f}%".replace(".", ","), annotation_position="top left")
    if 0 <= x["rasio_klaim"] <= 200:
        fig.add_trace(go.Scatter(x=[x["rasio_klaim"]], y=[p_now * 100], mode="markers",
                                 marker=dict(size=11, color=WARNA["t2"]), name="posisi saat ini",
                                 hovertemplate="Posisi saat ini: %{y:.1f}%<extra></extra>"))
    fig.update_xaxes(title="Rasio klaim t−1 (%)", ticksuffix="%")
    fig.update_yaxes(title="Probabilitas", ticksuffix="%", rangemode="tozero")
    fig.update_layout(showlegend=False)
    return _rapi(fig, 280)


def kontribusi(df: pd.DataFrame) -> go.Figure:
    warna = [WARNA["kritis"] if v > 0 else WARNA["baik"] for v in df["delta_log_odds"]]
    fig = go.Figure(go.Bar(x=df["delta_log_odds"], y=df["indikator"], orientation="h", marker_color=warna,
                           text=[f"{v:+.2f}".replace(".", ",") for v in df["delta_log_odds"]], textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x:+.2f} log-odds<extra></extra>"))
    m = max(0.5, float(df["delta_log_odds"].abs().max()) * 1.3)
    fig.update_xaxes(range=[-m, m], zeroline=True, zerolinecolor="rgba(90,100,110,0.6)")
    fig.update_yaxes(autorange="reversed")
    return _rapi(fig, 240)


def status_bar(df: pd.DataFrame) -> go.Figure:
    urut = list(STATUS_WARNA)
    hitung = df["status"].value_counts().reindex(urut, fill_value=0)
    fig = go.Figure(go.Bar(x=hitung.values, y=hitung.index, orientation="h",
                           marker_color=[STATUS_WARNA[s] for s in hitung.index], text=hitung.values,
                           textposition="outside", cliponaxis=False,
                           hovertemplate="%{y}: %{x} entitas<extra></extra>"))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, max(1, int(hitung.max())) * 1.15], dtick=1 if hitung.max() <= 10 else None)
    return _rapi(fig, 240)
