{ pkgs ? import <nixpkgs> {} }:
let
  version = "0.1";
in
pkgs.python3Packages.buildPythonPackage {
  name = "opp_env";
  src = ./.;

  SETUPTOOLS_SCM_PRETEND_VERSION = version;

  propagatedBuildInputs = with pkgs.python3Packages; [
    packaging
  ];

  build-system = with pkgs.python3Packages; [ setuptools-scm ];

  pythonImportsCheck = [
    "opp_env.database"
  ];

  doCheck = false;
}
