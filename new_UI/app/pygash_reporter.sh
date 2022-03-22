function install_pygash_reporter() {
    local path=${1}
    source /opt/rh/python27/enable

    case $(hostname --fqdn) in
      *.an.nuagenetworks.net|*.be.alcatel-lucent.com)
        local pypi_server="pypi.an.nuagenetworks.net"
        ;;
      *.ba.nuagenetworks.net|badc*)
        local pypi_server="pypi.ba.nuagenetworks.net"
        ;;
      *.ra.nuagenetworks.net|radc*)
        local pypi_server="radcreg.ra.nuagenetworks.net"
        ;;
      *.wf.nuagenetworks.net|wfdc*)
        local pypi_server="wfnupypi.wf.nuagenetworks.net"
        ;;
      *.bt.nuagenetworks.net|btdc*)
        local pypi_server="btnupypi.bt.nuagenetworks.net"
        ;;
      *)
        local pypi_server="pypi.mv.nuagenetworks.net"
        ;;
    esac

    /$(hostname -s)/ws/infra/regresstools/pygash_virtualenvs.sh \
        -a create \
        -i "http://${pypi_server}:3141/nuage/main/+simple" \
        -n pygashreporter \
        -p ${1}

    source ${1}/pygashreporter/bin/activate
    pip install -U pygashreporter
}

set -x
install_pygash_reporter ${1}
set +x
