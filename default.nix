{ pname
, version
, src
, python3Packages
, lib 
, nix
, curl
, git
, btar }:

python3Packages.buildPythonPackage {
  inherit version src pname;
  
  pyproject = true;
  disabled = python3Packages.pythonOlder "3.9";
  
  SETUPTOOLS_SCM_PRETEND_VERSION = version;

  propagatedBuildInputs = [ nix curl git btar ];

  nativeBuildInputs = [ python3Packages.setuptools-scm ];

  doCheck = true;
  pythonImportsCheck = [
    "opp_env.database"
  ];

  meta = with lib; {
    homepage= "https://github.com/omnetpp/opp_env";
    description = "Tool for Automated Installation of OMNeT++ Simulation Frameworks";
    longDescription = "opp_env is a powerful tool that allows for the easy and automated installation of OMNeT++ simulation frameworks and models, including dependencies like INET Framework and OMNeT++ itself. It can install any version of OMNeT++ and INET, as well as currently selected versions of Veins, SimuLTE, Simu5G and other models.";
    changelog = "https://github.com/omnetpp/opp_env/blob/${version}/CHANGES.md";
    license = licenses.lgpl3;
    maintainers = [ "rudi@omnetpp.org" ];
    platforms = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
  };
}
