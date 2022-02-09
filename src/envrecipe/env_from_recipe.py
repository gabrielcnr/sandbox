from conda_build.api import render
from conda_build.config import get_or_merge_config, Config

config = get_or_merge_config(Config())
metadata = render(".", config=config)

rundeps = metadata[0][0].ms_depends("run")

dep0 = rundeps[0]
dep0.conda_build_form()