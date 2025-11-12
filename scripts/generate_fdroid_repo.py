#!/usr/bin/env python3
"""
Generate F-Droid repository index from APK files
Uses only Python stdlib + aapt2 from Android SDK (no external dependencies)
"""

import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.dom import minidom

REPO_DIR = Path("repo")
REPO_NAME = "TikTok Redirect F-Droid Repository"
REPO_DESCRIPTION = "F-Droid repository for TikTok Redirect app - intercepts TikTok links and opens them in OffTikTok"
REPO_URL = "https://Mic92.github.io/TikTokRedirect/fdroid/repo"
REPO_ICON = "icon.png"


def get_file_hash(filepath: Path, algorithm: str = "sha256") -> str:
    """Calculate hash of a file"""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def find_aapt() -> str | None:
    """Find aapt or aapt2 in Android SDK"""
    # Check ANDROID_HOME environment variable
    android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")

    if android_home:
        build_tools = Path(android_home) / "build-tools"
        if build_tools.exists():
            # Get latest build-tools version
            versions = sorted(
                [d for d in build_tools.iterdir() if d.is_dir()], reverse=True
            )
            for version in versions:
                # Try aapt2 first (newer)
                for tool_name in ["aapt2", "aapt"]:
                    tool_path = version / tool_name
                    if tool_path.exists():
                        return str(tool_path)

    # Try system PATH
    for tool in ["aapt2", "aapt"]:
        try:
            result = subprocess.run(["which", tool], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

    return None


def parse_apk_with_aapt(apk_path: Path, aapt_path: str) -> dict[str, Any] | None:
    """Extract APK information using aapt/aapt2"""
    try:
        # Run aapt dump badging
        result = subprocess.run(
            [aapt_path, "dump", "badging", apk_path],
            capture_output=True,
            text=True,
            check=True,
        )

        output = result.stdout
        info = {}

        # Parse package info
        package_match = re.search(
            r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'",
            output,
        )
        if package_match:
            info["packagename"] = package_match.group(1)
            info["versioncode"] = package_match.group(2)
            info["versionname"] = package_match.group(3)
        else:
            print(f"Warning: Could not parse package info from {apk_path}")
            return None

        # Parse app name
        app_match = re.search(r"application-label:'([^']+)'", output)
        if app_match:
            info["appname"] = app_match.group(1)
        else:
            info["appname"] = info.get("packagename", "Unknown")

        # Parse SDK versions
        sdk_match = re.search(r"sdkVersion:'([^']+)'", output)
        if sdk_match:
            info["minsdkversion"] = sdk_match.group(1)
        else:
            info["minsdkversion"] = "21"  # Default

        target_match = re.search(r"targetSdkVersion:'([^']+)'", output)
        if target_match:
            info["targetsdkversion"] = target_match.group(1)
        else:
            info["targetsdkversion"] = "34"  # Default

        # Parse permissions
        permissions = re.findall(r"uses-permission: name='([^']+)'", output)
        info["permissions"] = permissions

        # Add file info
        info["size"] = os.path.getsize(apk_path)
        info["hash"] = get_file_hash(apk_path)
        info["filename"] = os.path.basename(apk_path)

        return info
    except subprocess.CalledProcessError as e:
        print(f"Error running aapt on {apk_path}: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error parsing APK {apk_path}: {e}")
        return None


def parse_apk(apk_path: Path) -> dict[str, Any] | None:
    """Extract information from APK using available tools"""
    # Find aapt
    aapt_path = find_aapt()

    if not aapt_path:
        print(
            "Error: aapt/aapt2 not found. Make sure Android SDK is installed and ANDROID_HOME is set."
        )
        return None

    print(f"Using {aapt_path} to parse APK")
    return parse_apk_with_aapt(apk_path, aapt_path)


def generate_index_xml(apks_info: list[dict[str, Any]]) -> ET.Element:
    """Generate index.xml for F-Droid repository"""
    root = ET.Element("fdroid")

    # Repository metadata
    repo = ET.SubElement(
        root,
        "repo",
        {
            "name": REPO_NAME,
            "icon": REPO_ICON,
            "url": REPO_URL,
            "version": "1",
            "timestamp": str(int(datetime.now().timestamp())),
        },
    )

    desc = ET.SubElement(repo, "description")
    desc.text = REPO_DESCRIPTION

    # Group APKs by package name
    packages: dict[str, list[dict[str, Any]]] = {}
    for apk_info in apks_info:
        pkg = apk_info["packagename"]
        if pkg not in packages:
            packages[pkg] = []
        packages[pkg].append(apk_info)

    # Generate application entries
    for pkg_name, versions in packages.items():
        # Sort by version code (latest first)
        versions.sort(key=lambda x: int(x["versioncode"]), reverse=True)
        latest = versions[0]

        app = ET.SubElement(root, "application", {"id": pkg_name})

        name = ET.SubElement(app, "name")
        name.text = latest["appname"]

        summary = ET.SubElement(app, "summary")
        summary.text = "Redirect TikTok links to OffTikTok"

        desc = ET.SubElement(app, "desc")
        desc.text = """
        TikTok Redirect automatically intercepts TikTok links and opens them in OffTikTok.
        
        Features:
        - Handles all TikTok domains (tiktok.com, vm.tiktok.com, vt.tiktok.com)
        - Opens content in embedded WebView
        - Preserves all URL parameters and fragments
        - Simple and lightweight
        """

        license_elem = ET.SubElement(app, "license")
        license_elem.text = "Apache-2.0"

        categories = ET.SubElement(app, "categories")
        category = ET.SubElement(categories, "category")
        category.text = "Internet"

        web = ET.SubElement(app, "web")
        web.text = REPO_URL.replace("/fdroid/repo", "")

        source = ET.SubElement(app, "source")
        source.text = REPO_URL.replace("/fdroid/repo", "")

        tracker = ET.SubElement(app, "tracker")
        tracker.text = REPO_URL.replace("/fdroid/repo", "") + "/issues"

        # Add all package versions
        for version in versions:
            package = ET.SubElement(app, "package")

            ver = ET.SubElement(package, "version")
            ver.text = version["versionname"]

            vercode = ET.SubElement(package, "versioncode")
            vercode.text = str(version["versioncode"])

            apkname = ET.SubElement(package, "apkname")
            apkname.text = version["filename"]

            hash_elem = ET.SubElement(package, "hash", {"type": "sha256"})
            hash_elem.text = version["hash"]

            size = ET.SubElement(package, "size")
            size.text = str(version["size"])

            sdkver = ET.SubElement(package, "sdkver")
            sdkver.text = str(version["minsdkversion"])

            added = ET.SubElement(package, "added")
            added.text = datetime.now().strftime("%Y-%m-%d")

            perms = ET.SubElement(package, "permissions")
            perms.text = ",".join(version["permissions"])

    return root


def generate_index_v1_json(apks_info: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate index-v1.json for modern F-Droid clients"""
    # Group APKs by package name
    packages: dict[str, dict[str, Any]] = {}
    for apk_info in apks_info:
        pkg = apk_info["packagename"]
        if pkg not in packages:
            packages[pkg] = {"metadata": apk_info, "versions": []}
        packages[pkg]["versions"].append(apk_info)

    repo_data: dict[str, Any] = {
        "repo": {
            "name": REPO_NAME,
            "description": REPO_DESCRIPTION,
            "icon": REPO_ICON,
            "address": REPO_URL,
            "timestamp": int(datetime.now().timestamp() * 1000),
        },
        "apps": [],
        "packages": {},
    }

    for pkg_name, data in packages.items():
        latest = max(data["versions"], key=lambda x: int(x["versioncode"]))

        app = {
            "packageName": pkg_name,
            "name": latest["appname"],
            "summary": "Redirect TikTok links to OffTikTok",
            "description": "TikTok Redirect automatically intercepts TikTok links and opens them in OffTikTok.\n\nFeatures:\n- Handles all TikTok domains\n- Opens in embedded WebView\n- Preserves URL parameters",
            "license": "Apache-2.0",
            "categories": ["Internet"],
            "webSite": REPO_URL.replace("/fdroid/repo", ""),
            "sourceCode": REPO_URL.replace("/fdroid/repo", ""),
            "issueTracker": REPO_URL.replace("/fdroid/repo", "") + "/issues",
            "added": int(datetime.now().timestamp() * 1000),
            "lastUpdated": int(datetime.now().timestamp() * 1000),
        }

        repo_data["apps"].append(app)

        package_versions = []
        for version in data["versions"]:
            pkg_entry = {
                "added": int(datetime.now().timestamp() * 1000),
                "apkName": version["filename"],
                "hash": version["hash"],
                "hashType": "sha256",
                "minSdkVersion": int(version["minsdkversion"]),
                "targetSdkVersion": int(version["targetsdkversion"]),
                "packageName": pkg_name,
                "sig": version["hash"][:16],  # Simplified signature
                "size": version["size"],
                "uses-permission": [{"name": p} for p in version["permissions"]],
                "versionCode": int(version["versioncode"]),
                "versionName": version["versionname"],
            }
            package_versions.append(pkg_entry)

        repo_data["packages"][pkg_name] = package_versions

    return repo_data


def main() -> None:
    """Main function to generate F-Droid repository index"""
    REPO_DIR.mkdir(parents=True, exist_ok=True)

    # Find all APKs in repo directory
    apk_files = list(REPO_DIR.glob("*.apk"))

    if not apk_files:
        print("No APK files found in repo directory")
        return

    print(f"Found {len(apk_files)} APK file(s)")

    # Parse all APKs
    apks_info = []
    for apk_path in apk_files:
        print(f"Processing {apk_path.name}...")
        info = parse_apk(apk_path)
        if info:
            apks_info.append(info)
            print(
                f"  ✓ {info['packagename']} v{info['versionname']} ({info['versioncode']})"
            )

    if not apks_info:
        print("No valid APK files found")
        return

    # Generate index.xml
    print("\nGenerating index.xml...")
    xml_root = generate_index_xml(apks_info)
    xml_string = minidom.parseString(ET.tostring(xml_root)).toprettyxml(indent="  ")

    with open("index.xml", "w") as f:
        f.write(xml_string)

    # Generate index-v1.json
    print("Generating index-v1.json...")
    json_data = generate_index_v1_json(apks_info)

    with open("index-v1.json", "w") as f:
        json.dump(json_data, f, indent=2)

    print(
        f"\n✅ Successfully generated F-Droid repository index with {len(apks_info)} package(s)"
    )
    print(f"Repository URL: {REPO_URL}")


if __name__ == "__main__":
    main()
