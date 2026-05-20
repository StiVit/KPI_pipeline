import os
import glob
from loader import load_data, get_path
from processor import clean_data
from kpi import KPIEngine
from ppt_builder import create_ppt
from visualization import visualize_kpis, get_output_path
from config import load_config
from dotenv import load_dotenv
from kpi_builder import test_config_gen

def find_kpi_config(config_folder):
    """
    Find the first YAML file with 'kpi' in the name from the config folder.
    """
    yaml_files = glob.glob(os.path.join(config_folder, "*.yaml"))
    kpi_files = [f for f in yaml_files if "kpi" in os.path.basename(f).lower()]

    if not kpi_files:
        raise FileNotFoundError(f"No YAML files with 'kpi' in the name found in {config_folder}")

    return kpi_files[0]

def main():
    load_dotenv()

    DATA_PATH = get_path()
    df = load_data(DATA_PATH, sheet_name="DB tot", header=2)
    df = clean_data(df)

    # Dynamic config file selection
    # config_folder = os.getenv("CONFIG_PATH", "../config")
    # config_path = find_kpi_config(config_folder)
    # config = load_config(config_path)
    config = test_config_gen()

    engine = KPIEngine(df, config)
    kpi_results = engine.compute_all()
    print([(kpi["name"], kpi["value"]) for kpi in kpi_results.values()])

    # Generate and save visualizations
    chart_paths = visualize_kpis(kpi_results)
    print("Charts saved to:", get_output_path())

    # TODO: Extract the images from the output/charts folder
    # create_ppt(kpis, ["data"])

if __name__ == "__main__":
    main()