from brownie import network, interface, TheVault, MyStrategy, web3
from _setup.config import REGISTRY
from helpers.constants import AddressZero
from rich.console import Console

console = Console()

ADMIN_SLOT = int(0xB53127684A568B3173AE13B9F8A6016E243E63B6E8EE1178D6A717850B5D6103)


## TODO: Paste Vault add here
## NOTE: Purposefully wrong for demo
VAULT = "0x63ad745506BD6a3E57F764409A47ed004BEc40b1"
STRATEGY = "0xC10bf5eC2e0d2A1A91E184ffEF228334B0c06023"


def main():
    """
    Checks that the proxyAdmin of all conracts added to the BadgerRegistry match
    the proxyAdminTimelock address on the same registry. How to run:

    1. Add all keys for the network's registry to the 'keys' array below.

    2. Add all authors' addresses with vaults added to the registry into the 'authors' array below.

    3. Add all all keys for the proxyAdmins for the network's registry paired to their owners' keys.

    4. Run the script and review the console output.
    """

    console.print("You are using the", network.show_active(), "network")

    # Get production registry
    registry = interface.IBadgerRegistry(REGISTRY)

    # Get proxyAdminTimelock
    proxyAdmin = registry.get("proxyAdminTimelock")
    assert proxyAdmin != AddressZero
    console.print("[cyan]proxyAdminTimelock:[/cyan]", proxyAdmin)

    vault = TheVault.at(VAULT)
    strategy = MyStrategy.at(STRATEGY)

    check_vault_and_strategy(vault, strategy, proxyAdmin, registry)



def check_vault_and_strategy(vault, strategy, proxyAdmin, registry):
    console.print("[blue]Checking proxyAdmins from vaults and strategies...[/blue]")

    name = vault.name()

    print("Checking for", name, vault.address)
    print("Strategy for", strategy.address)

    ## NOTE: Nuanced check frequently for keys
    strategist = registry.get("techOps")
    keeper = registry.get("keeper")
    governance = registry.get("governance")
    guardian = registry.get("guardian")
    treasury = registry.get("treasuryOps")


    # Get strategies from vaults and check vaults' proxyAdmins
    try:
        check_proxy_admin(vault, proxyAdmin)
        check_access_control(
            vault,
            strategist, keeper, governance, guardian, treasury
        )
    except Exception as error:
        print("Something went wrong")
        print(error)

    try:
        print("Check Strategy ProxyAdmin")
        check_proxy_admin(strategy, proxyAdmin)

        valid_or_warn(strategy.want(), vault.token(), "Vault and Strat token")
    except Exception as error:
        print("Something went wrong")
        print(error)


def check_proxy_admin(proxy, proxyAdmin):
    # Get proxyAdmin address form the proxy's ADMIN_SLOT
    val = web3.eth.getStorageAt(proxy.address, ADMIN_SLOT).hex()
    address = val

    # Check differnt possible scenarios
    if address == AddressZero:
        console.print("[red] admin not found on slot (GnosisSafeProxy?)[/red]")
    elif address != proxyAdmin:
        console.print(
            "[red] admin is different to proxyAdminTimelock[/red] - ", address
        )
    else:
        assert address == proxyAdmin
        console.print("[green] admin matches proxyAdminTimelock![/green]")


def check_access_control(vault, strategist, keeper, governance, guardian, treasury):
    valid_or_warn(vault.strategist(), strategist, "strategist")
    valid_or_warn(vault.keeper(), keeper, "keeper")
    valid_or_warn(vault.governance(), governance, "governance")
    valid_or_warn(vault.guardian(), guardian, "guardian")
    valid_or_warn(vault.treasury(), treasury, "treasury")



def valid_or_warn(value, expected, name):
    if value != expected:
        console.print(
            name, "[red] is different to [/red] - ", value, expected
        )
    else:
        assert value == expected
        console.print(name, "[green] matches ![/green]")