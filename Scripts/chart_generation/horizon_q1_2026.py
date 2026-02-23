"""
LIGHTHOUSE MACRO | RESEARCH CORE
Q1 2026: THE HIDDEN TRANSITION
Author: Bob Sheehan, CFA, CMT
Date: January 12, 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from pathlib import Path

# =============================================================================
# LIGHTHOUSE VISUAL STANDARDS
# =============================================================================

COLORS = {
    'ocean_blue': '#2389BB',
    'dusk_orange': '#FF6723',
    'electric_cyan': '#03DDFF',
    'hot_magenta': '#FF00F0',
    'sea_teal': '#289389',
    'silvs_gray': '#D1D1D1',
    'up_green': '#008000',
    'down_red': '#FF3333',
}

def apply_lighthouse_style():
    """Apply clean institutional charting standards."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 11,
        'axes.grid': False,
        'axes.spines.top': False,
        'axes.spines.right': True,
        'axes.spines.left': False,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'ytick.left': False,
        'ytick.right': True,
        'legend.fontsize': 9,
        'legend.frameon': False,
        'figure.figsize': (12, 7),
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
    })

apply_lighthouse_style()


def add_watermark(ax, fig):
    """Add Lighthouse watermarks: top-left and bottom-right."""
    fig.text(0.02, 0.98, 'LIGHTHOUSE MACRO', fontsize=8, color=COLORS['silvs_gray'],
             ha='left', va='top', alpha=0.7, fontweight='bold')
    fig.text(0.98, 0.02, '@LighthouseMacro', fontsize=8, color=COLORS['silvs_gray'],
             ha='right', va='bottom', alpha=0.7)


# =============================================================================
# MACRO ENGINE
# =============================================================================

class LighthouseMacroEngine:
    """Q1 2026 analytical engine."""

    def __init__(self):
        self.current_date = datetime(2026, 1, 12)

        # Current readings
        self.data = {
            'on_rrp': 3.3,                  # $B - effectively zero
            'bank_reserves': 2880,          # $B
            'gdp_nominal': 28100,           # $B (est)
            'sofr': 4.34,                   # %
            'effr': 4.33,                   # %
            '10y_yield': 4.79,              # %
            '30y_yield': 4.96,              # %
            'hy_oas': 276,                  # bps
            'vix': 18.07,                   #
            'move': 102.0,                  # est
            'quits_rate': 2.1,              # %
            'hires_rate': 3.3,              # %
            'unemployment_rate': 4.2,       # %
            'long_term_unemp_share': 0.236, # 23.6%
            # Stablecoin data (for SLI)
            'stablecoin_mcap': 205.0,       # $B current
            'stablecoin_mcap_30d_ago': 198.0,  # $B
            'stablecoin_mcap_90d_ago': 178.0,  # $B
        }

        # Historical baselines (5yr rolling where applicable)
        # Calibrated to match Horizon Jan 2026 report readings
        self.baselines = {
            'quits_mean': 2.8,              # Pre-pandemic avg ~2.8%, currently depressed
            'quits_std': 0.5,
            'hires_quits_mean': 1.55,       # Ratio baseline (hires typically 1.5-1.6x quits)
            'hires_quits_std': 0.15,
            'long_term_unemp_mean': 0.19,   # Pre-pandemic ~19%
            'long_term_unemp_std': 0.04,    # Wider band for structural variance
            'hy_oas_mean': 400,
            'hy_oas_std': 120,
            'vix_mean': 20,
            'vix_std': 5,
            'reserves_gdp_mean': 0.14,
            'reserves_gdp_std': 0.03,
            'stablecoin_growth_30d_mean': 0.02,  # 2% monthly growth baseline
            'stablecoin_growth_30d_std': 0.03,
        }

        self.thresholds = {
            'lclor': 2800,              # Lowest Comfortable Level of Reserves ($B)
            'reserves_gdp_warning': 0.12,
            'reserves_gdp_crisis': 0.08,
        }

    # -------------------------------------------------------------------------
    # PROPRIETARY INDICES
    # -------------------------------------------------------------------------

    def _zscore(self, value, mean, std):
        """Calculate z-score."""
        return (value - mean) / std if std != 0 else 0

    def calculate_lfi(self):
        """
        Labor Fragility Index.
        Avg(z(Long-Term%), z(-Quits), z(-Hires/Quits))
        Higher = more fragile. Inverted inputs capture "freezing not firing."
        """
        hires_quits = self.data['hires_rate'] / self.data['quits_rate']

        z_long_term = self._zscore(
            self.data['long_term_unemp_share'],
            self.baselines['long_term_unemp_mean'],
            self.baselines['long_term_unemp_std']
        )
        z_quits = -self._zscore(
            self.data['quits_rate'],
            self.baselines['quits_mean'],
            self.baselines['quits_std']
        )
        z_hires_quits = -self._zscore(
            hires_quits,
            self.baselines['hires_quits_mean'],
            self.baselines['hires_quits_std']
        )

        lfi = np.mean([z_long_term, z_quits, z_hires_quits])

        if lfi > 1.5:
            status = 'STRESS'
        elif lfi > 0.7:
            status = 'ELEVATED'
        else:
            status = 'HEALTHY'

        return round(lfi, 2), status

    def calculate_lci(self):
        """
        Liquidity Cushion Index.
        Z-score of (Reserves + RRP) / GDP vs historical.
        Negative = thin buffer.
        """
        total_liquidity = self.data['on_rrp'] + self.data['bank_reserves']
        liquidity_ratio = total_liquidity / self.data['gdp_nominal']

        lci = self._zscore(
            liquidity_ratio,
            self.baselines['reserves_gdp_mean'],
            self.baselines['reserves_gdp_std']
        )

        if lci < -1.0:
            status = 'STRESS RISK'
        elif lci < -0.3:
            status = 'THIN BUFFER'
        else:
            status = 'AMPLE'

        return round(lci, 2), status, round(liquidity_ratio * 100, 1)

    def calculate_clg(self, lfi):
        """
        Credit-Labor Gap.
        z(HY_OAS) - z(LFI). Negative = spreads too tight for labor reality.
        """
        z_hy = self._zscore(
            self.data['hy_oas'],
            self.baselines['hy_oas_mean'],
            self.baselines['hy_oas_std']
        )
        clg = z_hy - lfi

        if clg < -1.0:
            status = 'MISPRICED'
        elif clg < 0:
            status = 'STRETCHED'
        else:
            status = 'FAIR'

        return round(clg, 2), status

    def calculate_sli(self):
        """
        Stablecoin Liquidity Impulse.
        Rate of change in stablecoin market cap — proxy for on-chain liquidity
        and marginal T-bill demand. Positive = liquidity injection, Negative = drain.

        We track both 30d momentum and 90d trend for regime context.
        """
        mcap = self.data['stablecoin_mcap']
        mcap_30d = self.data['stablecoin_mcap_30d_ago']
        mcap_90d = self.data['stablecoin_mcap_90d_ago']

        # 30-day rate of change (annualized)
        roc_30d = (mcap - mcap_30d) / mcap_30d
        roc_30d_ann = roc_30d * 12

        # 90-day rate of change (annualized)
        roc_90d = (mcap - mcap_90d) / mcap_90d
        roc_90d_ann = roc_90d * 4

        # SLI = z-score of 30d momentum
        sli = self._zscore(
            roc_30d,
            self.baselines['stablecoin_growth_30d_mean'],
            self.baselines['stablecoin_growth_30d_std']
        )

        # Status based on impulse direction and magnitude
        if sli > 1.0:
            status = 'SURGING'
        elif sli > 0.3:
            status = 'EXPANDING'
        elif sli > -0.3:
            status = 'NEUTRAL'
        elif sli > -1.0:
            status = 'CONTRACTING'
        else:
            status = 'DRAINING'

        return round(sli, 2), status, {
            'mcap_current': mcap,
            'roc_30d': round(roc_30d * 100, 1),
            'roc_30d_ann': round(roc_30d_ann * 100, 1),
            'roc_90d_ann': round(roc_90d_ann * 100, 1),
        }

    def calculate_mri(self, lfi, lci, sli=None):
        """
        Macro Risk Index.
        Composite: Labor fragility + Liquidity stress - Credit/Vol complacency.
        Optional SLI component for crypto liquidity signal.
        Higher = more defensive positioning warranted.
        """
        z_credit = self._zscore(
            self.data['hy_oas'],
            self.baselines['hy_oas_mean'],
            self.baselines['hy_oas_std']
        )
        z_vol = self._zscore(
            self.data['vix'],
            self.baselines['vix_mean'],
            self.baselines['vix_std']
        )

        # MRI: fragility + liquidity stress, offset by credit/vol "cushion"
        # SLI adds signal: negative SLI = crypto draining = additional risk
        if sli is not None:
            mri = (
                (0.30 * lfi) +
                (0.30 * -lci) +
                (0.15 * -z_credit) +
                (0.15 * -z_vol) +
                (0.10 * -sli)  # Negative SLI adds to risk
            )
        else:
            mri = (0.35 * lfi) + (0.35 * -lci) + (0.15 * -z_credit) + (0.15 * -z_vol)

        if mri > 1.0:
            status = 'DEFENSIVE'
        elif mri > 0.5:
            status = 'CAUTIOUS'
        else:
            status = 'CONSTRUCTIVE'

        return round(mri, 2), status

    # -------------------------------------------------------------------------
    # VISUALIZATIONS
    # -------------------------------------------------------------------------

    def plot_reserves_danger_zone(self):
        """Bank Reserves/GDP with crisis zones."""
        dates = pd.date_range(start='2017-01-01', end='2026-03-31', freq='ME')

        # Synthetic path: 2019 crisis, COVID spike, QT decline
        values = []
        for d in dates:
            if d < datetime(2019, 9, 1):
                val = 0.11 + np.random.normal(0, 0.005)
            elif d < datetime(2020, 3, 1):
                val = 0.10 + np.random.normal(0, 0.003)  # Sept 2019 stress
            elif d < datetime(2021, 1, 1):
                val = 0.10 + (d - datetime(2020, 3, 1)).days / 300 * 0.08
            elif d < datetime(2022, 6, 1):
                val = 0.18 + np.random.normal(0, 0.005)
            elif d < datetime(2026, 1, 1):
                months_since = (d.year - 2022) * 12 + d.month - 6
                val = 0.18 - months_since * 0.002 + np.random.normal(0, 0.003)
            else:
                val = 0.103
            values.append(max(val * 100, 8))

        df = pd.DataFrame({'Date': dates, 'Reserves_GDP': values})

        fig, ax = plt.subplots()

        # Zones first (background)
        ax.axhspan(0, 8, color=COLORS['down_red'], alpha=0.15, label='Crisis (<8%)')
        ax.axhspan(8, 12, color=COLORS['dusk_orange'], alpha=0.15, label='Warning (8-12%)')
        ax.axhspan(12, 22, color=COLORS['sea_teal'], alpha=0.10, label='Comfortable (>12%)')

        # Data
        ax.plot(df['Date'], df['Reserves_GDP'], color=COLORS['ocean_blue'],
                linewidth=2, label='Reserves/GDP')

        # Current marker
        current_val = 10.3
        ax.scatter([self.current_date], [current_val], color=COLORS['down_red'],
                   s=100, zorder=5, edgecolor='white', linewidth=1.5)
        ax.annotate(f'{current_val}%', (self.current_date, current_val),
                    xytext=(10, 10), textcoords='offset points',
                    fontweight='bold', color=COLORS['down_red'], fontsize=11)

        # Sept 2019 annotation
        ax.annotate('Sept 2019\nRepo Crisis', (datetime(2019, 9, 15), 10.5),
                    fontsize=8, ha='center', color=COLORS['silvs_gray'])

        ax.set_title('Reserves Entering the Warning Zone')
        ax.set_ylabel('Bank Reserves (% GDP)', labelpad=10)
        ax.set_ylim(6, 20)
        ax.yaxis.set_label_position('right')
        ax.legend(loc='upper left', framealpha=0.9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        add_watermark(ax, fig)
        plt.tight_layout()
        return fig

    def plot_k_shaped_savings(self):
        """Two-speed consumer: excess savings by cohort."""
        cohorts = ['Top 20%', 'Middle 60%', 'Bottom 20%']
        excess_savings = [480, -180, -250]
        colors = [COLORS['sea_teal'], COLORS['dusk_orange'], COLORS['down_red']]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(cohorts, excess_savings, color=colors, width=0.6,
                      edgecolor='white', linewidth=2)

        ax.axhline(0, color=COLORS['silvs_gray'], linewidth=1.5, linestyle='-')

        for bar, val in zip(bars, excess_savings):
            offset = 25 if val > 0 else -45
            ax.text(bar.get_x() + bar.get_width()/2, val + offset,
                    f'${val:+,}B', ha='center', fontweight='bold', fontsize=12)

        ax.set_title('The K-Shaped Canyon: Excess Savings (Jan 2026)')
        ax.set_ylabel('vs Pre-Pandemic Trend ($B)', labelpad=10)
        ax.yaxis.set_label_position('right')
        ax.set_ylim(-350, 550)

        # Annotations
        ax.text(0, 520, 'Still buffered', ha='center', fontsize=9,
                color=COLORS['sea_teal'], style='italic')
        ax.text(2, -310, 'Borrowing to survive', ha='center', fontsize=9,
                color=COLORS['down_red'], style='italic')

        add_watermark(ax, fig)
        plt.tight_layout()
        return fig

    def plot_stress_calendar(self):
        """Q1 2026 liquidity stress timeline."""
        events = [
            ('Jan 15', 'Tax Payments', 2),
            ('Jan 29', 'FOMC', 2),
            ('Feb 15', 'Refunding', 3),
            ('Mar 15', 'Debt Ceiling', 3),
            ('Apr 15', 'Tax Day', 4),
        ]

        dates = [e[0] for e in events]
        labels = [e[1] for e in events]
        stress = [e[2] for e in events]

        fig, ax = plt.subplots(figsize=(10, 5))

        # Color gradient based on stress
        colors = [COLORS['dusk_orange'] if s <= 2 else
                  COLORS['hot_magenta'] if s == 3 else
                  COLORS['down_red'] for s in stress]

        bars = ax.bar(dates, stress, color=colors, width=0.6,
                      edgecolor='white', linewidth=2)

        for i, (bar, label) in enumerate(zip(bars, labels)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                    label, ha='center', fontweight='bold', fontsize=9)

        ax.set_title('Q1 2026: The 16-Week Stress Window')
        ax.set_ylabel('Stress Intensity', labelpad=10)
        ax.yaxis.set_label_position('right')
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(['Low', 'Moderate', 'Elevated', 'High'])

        add_watermark(ax, fig)
        plt.tight_layout()
        return fig

    # -------------------------------------------------------------------------
    # DASHBOARD
    # -------------------------------------------------------------------------

    def generate_dashboard(self, include_sli=True):
        """Print executive summary."""
        lfi, lfi_status = self.calculate_lfi()
        lci, lci_status, liq_ratio = self.calculate_lci()
        clg, clg_status = self.calculate_clg(lfi)
        sli, sli_status, sli_data = self.calculate_sli()
        mri, mri_status = self.calculate_mri(lfi, lci, sli if include_sli else None)

        date_str = self.current_date.strftime('%b %d, %Y').upper()

        print()
        print('=' * 65)
        print(f'  LIGHTHOUSE MACRO | EXECUTIVE DASHBOARD | {date_str}')
        print('=' * 65)
        print(f'  REGIME: THE SILENT STOP / LIQUIDITY TWILIGHT ZONE')
        print('-' * 65)
        print(f'  LFI (Labor Fragility):    {lfi:+.2f}  [{lfi_status}]')
        print(f'  LCI (Liquidity Cushion):  {lci:+.2f}  [{lci_status}]')
        print(f'  CLG (Credit-Labor Gap):   {clg:+.2f}  [{clg_status}]')
        print(f'  SLI (Stablecoin Impulse): {sli:+.2f}  [{sli_status}]')
        print(f'  MRI (Macro Risk):         {mri:+.2f}  [{mri_status}]')
        print('-' * 65)
        print('  KEY LEVELS:')
        print(f'  Bank Reserves:      ${self.data["bank_reserves"]:,}B  (Floor: ${self.thresholds["lclor"]:,}B)')
        print(f'  Reserves/GDP:       {liq_ratio}%  (Warning: <12%)')
        print(f'  HY OAS:             {self.data["hy_oas"]} bps  (17th %ile)')
        print(f'  Long-Term Unemp:    {self.data["long_term_unemp_share"]*100:.1f}%  (Structural)')
        print('-' * 65)
        print('  STABLECOIN LIQUIDITY:')
        print(f'  Market Cap:         ${sli_data["mcap_current"]}B')
        print(f'  30d Change:         {sli_data["roc_30d"]:+.1f}%  ({sli_data["roc_30d_ann"]:+.1f}% ann.)')
        print(f'  90d Change (ann.):  {sli_data["roc_90d_ann"]:+.1f}%')
        print('=' * 65)
        print()

        return {
            'lfi': (lfi, lfi_status),
            'lci': (lci, lci_status),
            'clg': (clg, clg_status),
            'sli': (sli, sli_status, sli_data),
            'mri': (mri, mri_status),
            'date': self.current_date,
        }


# =============================================================================
# EXECUTION
# =============================================================================

if __name__ == '__main__':
    engine = LighthouseMacroEngine()

    # Dashboard
    metrics = engine.generate_dashboard()

    # Charts
    fig1 = engine.plot_reserves_danger_zone()
    fig2 = engine.plot_k_shaped_savings()
    fig3 = engine.plot_stress_calendar()

    plt.show()
