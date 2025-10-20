"""
Color schemes and banner for terminal output.
"""


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INFO = '\033[97m'
    
    # Extended colors
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'


def print_banner():
    """Print application banner."""
    banner = f"""{Colors.CYAN}
    ╦ ╦┬┌─┐┬╔╗ ┬─┐┌─┐┌─┐┬┌─┌─┐┬─┐  ╔═╗┬─┐┌─┐
    ║║║│├┤ │╠╩╗├┬┘├┤ ├─┤├┴┐├┤ ├┬┘  ╠═╝├┬┘│ │
    ╚╩╝┴└  ┴╚═╝┴└─└─┘┴ ┴┴ ┴└─┘┴└─  ╩  ┴└─└─┘{Colors.ENDC}
    
    {Colors.BOLD}Automated WiFi Auditing Suite v1.0{Colors.ENDC}
    {Colors.INFO}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}
    {Colors.WARNING}⚠  Solo para uso educativo y auditorías autorizadas{Colors.ENDC}
    {Colors.INFO}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.ENDC}
    """
    print(banner)


def print_section_header(title):
    """Print a section header."""
    print(f"\n{Colors.HEADER}╔{'═' * (len(title) + 2)}╗{Colors.ENDC}")
    print(f"{Colors.HEADER}║ {title} ║{Colors.ENDC}")
    print(f"{Colors.HEADER}╚{'═' * (len(title) + 2)}╝{Colors.ENDC}\n")


def print_success(message):
    """Print success message."""
    print(f"{Colors.SUCCESS}[✓] {message}{Colors.ENDC}")


def print_error(message):
    """Print error message."""
    print(f"{Colors.FAIL}[✗] {message}{Colors.ENDC}")


def print_info(message):
    """Print info message."""
    print(f"{Colors.INFO}[i] {message}{Colors.ENDC}")


def print_warning(message):
    """Print warning message."""
    print(f"{Colors.WARNING}[!] {message}{Colors.ENDC}")


def print_progress(message):
    """Print progress message."""
    print(f"{Colors.OKCYAN}[*] {message}{Colors.ENDC}")