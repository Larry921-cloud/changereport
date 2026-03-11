"""Telecom/IT jargon to layman's terms translation engine."""

import re
import pandas as pd


# Tier 1: Category context descriptions
CATEGORY_LAYMAN = {
    "Radio Network": "the mobile/cell tower network (wireless signal and coverage)",
    "IP Core": "the central internet routing infrastructure (carries data traffic)",
    "Packet Core": "the core mobile data processing system (manages phone and internet connections)",
    "Transmission Network": "the backbone network links (fiber/microwave connecting sites together)",
    "Systems and IT": "internal IT systems and business applications",
    "Software Engineering": "software development and deployment systems",
    "Cyber Security": "security systems protecting the network from threats",
    "Billing and Revenue": "customer billing and payment processing systems",
}

# Tier 2: Keyword/phrase replacement dictionary
JARGON_MAP = {
    # Network elements
    r"\bRAN\b": "radio access network (cell towers)",
    r"\beNodeB\b": "4G cell tower equipment",
    r"\bgNodeB\b": "5G cell tower equipment",
    r"\bNR3600\b": "5G 3600MHz radio frequency band",
    r"\bNR700\b": "5G 700MHz radio frequency band",
    r"\bNR\b(?!\d)": "5G New Radio",
    r"\bLTE\b": "4G LTE",
    r"\bL1800\b": "4G 1800MHz frequency band",
    r"\b4G\b": "4G",
    r"\b5G\b": "5G",
    r"\bVoLTE\b": "Voice over 4G (HD calling)",
    r"\bSRVCC\b": "call handover from 4G to 3G/2G",
    r"\bIRAT\b": "handover between different network technologies",
    r"\bMME\b": "mobile connection manager",
    r"\bePDG\b": "WiFi-to-mobile gateway",
    r"\bUPCF\b": "user policy control function",
    r"\bCBS\b": "convergent billing system",
    r"\bRTN\b": "radio transmission network (microwave links)",
    r"\bOSN\s*1800\b": "optical switching equipment (OSN 1800)",
    r"\bNCE\b": "network cloud engine (management platform)",
    r"\bU2020\b": "Huawei network management system",
    r"\bAPN\b": "access point name (network connection point)",
    r"\bENNI\b": "external network-to-network interface (connection between carriers)",

    # Protocols & technologies
    r"\bBGP\b": "internet route management protocol (BGP)",
    r"\bOSPF\b": "internal network routing protocol",
    r"\bMPLS\b": "high-speed network routing technology",
    r"\bVLAN\b": "virtual network segment",
    r"\bDNS\b": "domain name system (website address lookup)",
    r"\bDHCP\b": "automatic IP address assignment",
    r"\bIPSec\b": "encrypted network tunnel",
    r"\bVPN\b": "secure private network connection",
    r"\bQoS\b": "quality of service (traffic priority)",
    r"\bSLA\b": "service level agreement",
    r"\bMML\b": "network configuration commands",
    r"\bXML\b": "configuration data format",
    r"\bCDN\b": "content delivery network (speeds up web access)",
    r"\bsFTP\b": "secure file transfer",
    r"\bHTTPS\b": "secure web traffic",
    r"\bNAT\b": "network address translation",
    r"\bPLMN\b": "mobile network operator identifier",
    r"\bK8s?\b": "Kubernetes (container platform)",
    r"\bSSL\b": "secure connection certificate",

    # Equipment & systems
    r"\bNE8K\b": "Huawei NE8000 router",
    r"\bNE8000\b": "Huawei NE8000 router",
    r"\bUSC\b": "unified security controller",
    r"\bAxiom\b": "Axiom billing platform",
    r"\bGitLab\b": "GitLab software development platform",
    r"\bArgoCD\b": "ArgoCD automated deployment tool",
    r"\bTerraform\b": "Terraform infrastructure automation tool",
    r"\bAzure\b": "Microsoft Azure cloud platform",

    # Actions & concepts
    r"\bcutover\b": "switchover to new system",
    r"\bfailover\b": "automatic switch to backup",
    r"\brollback\b": "reverting to previous configuration",
    r"\bpatching\b": "applying software updates",
    r"\bfirmware\b": "device software",
    r"\bprovisioning\b": "setting up and configuring",
    r"\bdecommission(?:ing)?\b": "retiring/removing from service",
    r"\bmigrat(?:e|ion|ing)\b": "moving to a new system",
    r"\bcommission(?:ing)?\b": "bringing into service",
    r"\bKPI\b": "key performance indicator",
    r"\bNPO\b": "network performance optimization team",
    r"\bNOC\b": "network operations center",
    r"\bCAB\b": "change advisory board",
    r"\bMOP\b": "method of procedure (step-by-step plan)",
    r"\be-tilt\b": "electronic antenna tilt angle",
    r"\btilt\b": "antenna angle adjustment",
    r"\bazimuth\b": "antenna direction/orientation",
    r"\b256QAM\b": "high-efficiency data encoding (256QAM)",
    r"\bbandwidth\b": "network capacity",
    r"\bthroughput\b": "data transfer speed",
    r"\bredundancy\b": "backup/failsafe capability",
    r"\blatency\b": "delay/response time",
    r"\bprefix(?:es)?\b": "network address range(s)",
    r"\bPE\b": "provider edge router",
    r"\bfull-mesh\b": "fully interconnected network",
    r"\bvpnv4\b": "VPN routing protocol (VPNv4)",
}

# Impact level translations
IMPACT_LAYMAN = {
    "No Impact": "no disruption expected for customers",
    "Site Down": "a cell site will be temporarily offline, potentially affecting coverage in a localized area",
    "Users Disconnected": "some users may experience brief disconnections",
    "Degradation in Service": "service quality may be temporarily reduced (slower speeds or intermittent issues)",
    "Application Unavailable / Reset / Restart": "a business application will be temporarily unavailable",
    "Application Unavailable": "a business application will be temporarily unavailable",
}


def translate_change(row: pd.Series) -> str:
    """Produce a plain-English summary of one change record."""
    parts = []

    # What area
    cat = str(row.get("category", "")).strip()
    cat_desc = CATEGORY_LAYMAN.get(cat, cat)
    if cat_desc:
        parts.append(f"This change relates to {cat_desc}.")

    # What is being done
    subject = str(row.get("subject", "")).strip()
    if subject:
        translated_subject = _apply_jargon_map(subject)
        parts.append(f"The work involved: {translated_subject}.")

    # Why
    reason = str(row.get("reason_benefit", "")).strip()
    if reason and reason not in ("", "N/A", "n/a", "See attached"):
        translated_reason = _apply_jargon_map(reason)
        parts.append(f"Purpose: {translated_reason}.")

    # Impact
    impact = str(row.get("impact_description", "No Impact")).strip()
    impact_plain = IMPACT_LAYMAN.get(impact, impact)
    if impact_plain:
        parts.append(f"Expected customer impact: {impact_plain}.")

    # Duration
    duration = row.get("duration_hours")
    if pd.notna(duration):
        try:
            dur = float(duration)
            if dur < 1:
                parts.append(f"Duration: approximately {int(dur * 60)} minutes.")
            else:
                parts.append(f"Duration: approximately {dur:.1f} hours.")
        except (ValueError, TypeError):
            pass

    return " ".join(parts)


def _apply_jargon_map(text: str) -> str:
    """Apply regex-based jargon replacements to text."""
    result = text
    for pattern, replacement in JARGON_MAP.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result
