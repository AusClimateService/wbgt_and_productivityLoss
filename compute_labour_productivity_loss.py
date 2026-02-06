"""
Labour Productivity Loss (Fit-for-Purpose to support delivery to Treasury)
=================================================================================

Compute gridded labour productivity loss (fractional loss (0..1)) from hourly WBGT for three physical
intensity classes (low/medium/high). This is fit-for-purpose ACS code intended
to support delivery to Treasury, not a general-purpose library.

Unit
--------
The computation returns a fraction in [0, 1] (0 = no loss, 1 = 100% loss).

Examples
--------
1. hard-code input arguments under "Main" manually (this can be modified for future purposes to enable argument parsing)
2. Run PBS job:
python compute_labour_productivity_loss.py 

# For plotting 
Results can be multiplied by -100 in a post-processing step to obtain "change in labour productivity" in %.
"""


import xarray as xr
import numpy as np
from scipy.special import erf
from pathlib import Path

var = "wbgtAdjust" # wbgt for reference

# Labour productivity function parameters by physical intensity
physical_intensity = {
    "low":    {"omega": 35.5, "mu": 3.9},
    "medium": {"omega": 33.5, "mu": 3.9},
    "high":   {"omega": 32.5, "mu": 4.2},
}

# Labour productivity loss
def labour_productivity_damage(wbgt, omega, mu):
    """
    Fractional loss in labour productivity in [0, 1].

    Parameters
    ----------
    wbgt : xr.DataArray
        Wet Bulb Globe Temperature (degC).
    omega : float
        physical-intensity-dependent parameter (see above).
    mu : float
        physical-intensity-dependent parameter (see above).

    Returns
    -------
    xr.DataArray
        Fraction in [0, 1], where 1 = 100% loss.
    """
    return 0.5 * (
        1.0 + erf((wbgt - omega) / (mu * np.sqrt(2.0)))
    )

# Process yearly wbgtAdjust files
def process_file(input_nc, output_nc):
    """
    Process a single NetCDF file and write productivity-loss outputs.
    """
    print(f"Processing {input_nc.name}")

    ds = xr.open_dataset(
        input_nc, engine='netcdf4',chunks={}
    )

    wbgt = ds[var]

    # Compute fractional losses (0..1)
    productivity_loss_low = labour_productivity_damage(
        wbgt,
        physical_intensity["low"]["omega"],
        physical_intensity["low"]["mu"]
    )

    productivity_loss_medium = labour_productivity_damage(
        wbgt,
        physical_intensity["medium"]["omega"],
        physical_intensity["medium"]["mu"]
    )

    productivity_loss_high = labour_productivity_damage(
        wbgt,
        physical_intensity["high"]["omega"],
        physical_intensity["high"]["mu"]
    )

    # output
    out_ds = xr.Dataset(
        {
            "productivity_loss_low": productivity_loss_low,
            "productivity_loss_medium": productivity_loss_medium,
            "productivity_loss_high": productivity_loss_high,
        },
        coords=ds.coords,
        attrs={
            "title": "Hourly labour productivity damage due to humid heat stress",
            "source": "WBGT bias-adjusted input, IGR damage function",
            "units": "change in labour productivity",
            "references": (
                "Roson & Sartori (2016); "
                "ILO (2019); "
                "Kjellstrom et al. (2009); "
                "Kompas et al (2018)"
            ),
        },
    )

    # attributes
    out_ds["productivity_loss_low"].attrs.update(
        long_name="Labour productivity loss (low physical intensity)",
        units="1",
    )
    out_ds["productivity_loss_medium"].attrs.update(
        long_name="Labour productivity loss (medium physical intensity)",
        units="1",
    )
    out_ds["productivity_loss_high"].attrs.update(
        long_name="Labour productivity loss (high physical intensity)",
        units="1",
    )

    # write uncompressed and unchunked files
    out_ds = out_ds.unify_chunks().load()
    out_ds.to_netcdf(output_nc, engine="netcdf4")

    print(f"Written {output_nc.name}\n")


# Batch runner
def run_batch(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    files = sorted(input_dir.glob(f"{var}_*.nc"))

    for f in files:
        out_file = output_dir / f.name.replace(
            var, "productivityLoss"
        )
        process_file(f, out_file)

# Main
if __name__ == "__main__":

    inst = "BOM" #"BOM" #"CSIRO"
    if inst =="CSIRO":
        version = "v20251120"
    else:
        version = "v20250901"        
    gcm= "ACCESS-ESM1-5"
    run = "r6i1p1f1"    
    rcm = "BARPA-R" #"BARPA-R" #"CCAM-v2203-SN"
    ssps = ["historical", "ssp126", "ssp370"]
    for ssp in ssps:
        ### Reference
        # input_dir=f"/g/data/ia39/australian-climate-service/test-data/CORDEX/output-CMIP6/bias-adjusted-output/AUST-11i/{inst}/{gcm}/{ssp}/{run}/{rcm}/v1-r1-ACS-QME-BARRAR2-1980-2022/1hr/{var}/{version}/"
        # output_dir=f"/scratch/xv83/at2708/productivityLoss/AUST-11i/{inst}/{gcm}/{ssp}/{run}/{rcm}/v1-r1-ACS-QME-BARRAR2-1980-2022/1hr/productivityLoss/{version}/"
        ### Models
        input_dir=f"/g/data/ia39/australian-climate-service/test-data/BARRA2/output/reanalysis/AUST-11/BOM/ERA5/historical/hres/BARRAR2/v1/1hr/wbgt/v20250901-native-contiguous/"
        output_dir=f"/scratch/xv83/at2708/productivityLoss/BOM/ERA5/historical/hres/BARRAR2/v1/1hr/productivityLoss/v20250901-native-contiguous/"

        print(f"SSP: {ssp}")
        print(f"Input : {input_dir}")
        print(f"Output: {output_dir}")

        run_batch(
            input_dir=input_dir,
            output_dir=output_dir
        )


