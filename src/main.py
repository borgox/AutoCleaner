"""
A beautiful, fast, and feature-rich file organization tool.
"""

import os
import random
import sys
import time
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse

# Third-party imports
try:
    import rich
    from rich.console import Console
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.tree import Tree
    from rich.layout import Layout
    from rich.live import Live
    import questionary
    from questionary import Style
except ImportError as e:
    print(f"Missing required packages. Install with: pip install rich questionary")
    sys.exit(1)

# Initialize rich console
console = Console()

@dataclass
class FileInfo:
    """Enhanced file information structure"""
    name: str
    full_path: str
    size_bytes: int
    size_human: str
    created: str
    modified: str
    accessed: str
    extension: str
    category: Optional[str] = None
    
    @classmethod
    def from_path(cls, file_path: Path) -> 'FileInfo':
        """Create FileInfo from a Path object"""
        stats = file_path.stat()
        return cls(
            name=file_path.name,
            full_path=str(file_path),
            size_bytes=stats.st_size,
            size_human=format_bytes(stats.st_size),
            created=datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            modified=datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            accessed=datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
            extension=file_path.suffix.lower().lstrip('.')
        )

@dataclass 
class OrganizationResult:
    """Results of the organization process"""
    total_files: int
    organized_files: int
    skipped_files: int
    categories_created: List[str]
    total_size: int
    processing_time: float
    files_by_category: Dict[str, List[FileInfo]]


FILE_CATEGORIES = {
    "📁 Archives": [
        "zip", "rar", "7z", "tar", "gz", "xz", "bz2", "lz", "lzma", "cab", "zst", "ace", "arj",
        "lha", "lzh", "z", "tgz", "tbz2", "txz", "tlz", "taz", "tz", "deb", "rpm", "xar", "dmg",
        "sit", "sitx", "sea", "hqx", "cpt", "pit", "now", "bh", "lbr", "mar", "pak", "partimg"
    ],
    "🎮 Games": [
        "iso", "bin", "cue", "pak", "obb", "rom", "sav", "nds", "rpf", "vpk", "wad", "xci", "nsp", 
        "uasset", "bsa", "esp", "esm", "gba", "nds", "3ds", "cia", "gcm", "gcz", "wbfs", "rvz",
        "cso", "pbp", "psv", "vdf", "dat", "p3t", "pkg", "rap", "rif", "sfo", "self", "elf",
        "prx", "at3", "at9", "oma", "aa3", "psarc", "big", "forge", "unity3d", "assets",
        "bundle", "resource", "bank", "sb", "usm", "cpk", "arc", "res", "pak", "wad", "lvl"
    ],
    "🌐 Torrents": [
        "torrent", "aria2", "utmetadata", "btsearch", "btskin", "magnet", "bt", "bc!", "ut",
        "!bt", "incomplete", "temp", "crdownload", "partial", "opdownload", "download"
    ],
    "🖼️ Images": [
        "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "tif", "svg", "ico", "heic", "heif",
        "raw", "nef", "cr2", "cr3", "crw", "psd", "psb", "xcf", "ai", "eps", "dng", "orf", "rw2",
        "arw", "sr2", "srf", "raf", "3fr", "ari", "bay", "cap", "iiq", "eip", "dcs", "dcr",
        "drf", "k25", "kdc", "erf", "fff", "mef", "mos", "mrw", "ptx", "pxn", "r3d", "rwl",
        "rwz", "x3f", "avif", "jxl", "pcx", "tga", "ppm", "pgm", "pbm", "pnm", "xbm", "xpm",
        "cut", "emf", "wmf", "cgm", "pic", "pict", "mac", "qti", "qtif", "sgi", "ras", "sun",
        "pdd", "skp", "dds", "hdr", "exr", "pfm", "fli", "flc", "ani", "cur"
    ],
    "🎬 Videos": [
        "webm", "mkv", "flv", "vob", "ogv", "ogg", "gifv", "mng", "mov", "avi", "qt", "wmv", 
        "yuv", "rm", "rmvb", "asf", "amv", "mp4", "m4p", "m4v", "mpg", "mp2", "mpeg", "mpe", 
        "mpv", "svi", "3gp", "3g2", "mxf", "roq", "nsv", "f4v", "f4p", "f4a", "f4b", "mod", 
        "mts", "m2ts", "ts", "divx", "xvid", "dv", "m1v", "m2v", "m4u", "mj2", "mjpg", "mjpeg",
        "nuv", "rv", "m3u8", "webvtt", "vtt", "srt", "sub", "idx", "ssa", "ass", "usf", "ssf",
        "rt", "sbv", "ttml", "dfxp", "scc", "stl", "cap", "scr", "smi", "sami"
    ],
    "🎵 Audio": [
        "mp3", "wav", "flac", "aac", "ogg", "oga", "wma", "m4a", "opus", "alac", "aiff", "aif",
        "aifc", "mid", "midi", "kar", "amr", "awb", "au", "snd", "ra", "ram", "ac3", "dts",
        "ape", "wv", "tta", "tak", "spx", "mka", "dff", "dsf", "caf", "rf64", "w64", "bwf",
        "cda", "gym", "it", "s3m", "xm", "mod", "669", "amf", "ams", "dbm", "dmf", "dsm",
        "far", "mdl", "med", "mtm", "okt", "ptm", "stm", "ult", "uni", "mt2", "psm", "umx",
        "plm", "mo3", "xmz", "itz", "s3z", "miz", "sid", "nsf", "spc", "vgm", "psf", "minipsf"
    ],
    "📄 Documents": [
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "rtf", "md", "csv", "odt", 
        "ods", "odp", "pages", "numbers", "key", "tex", "epub", "mobi", "azw", "azw3", "azw4",
        "lit", "pdb", "fb2", "tcr", "prc", "lrf", "oxps", "xps", "djvu", "djv", "cbr", "cbz",
        "cb7", "cbt", "cba", "chm", "hlp", "wri", "wpd", "abw", "zabw", "aw", "sxw", "stw",
        "sxc", "stc", "sxi", "sti", "sxd", "std", "sxg", "sxm", "mml", "mathml", "fodp",
        "fods", "fodt", "fodg", "uot", "uos", "uop", "docm", "dotx", "dotm", "xlsm", "xltx",
        "xltm", "xlsb", "xlam", "pptm", "potx", "potm", "ppam", "ppsx", "ppsm", "sldx", "sldm"
    ],
    "💻 Code": [
        "py", "js", "ts", "java", "cpp", "c", "cs", "go", "rs", "rb", "php", "html", "css", 
        "json", "xml", "sh", "bat", "pl", "lua", "ipynb", "sql", "yml", "yaml", "toml", "kt",
        "swift", "dart", "r", "m", "h", "hpp", "jsx", "tsx", "vue", "scss", "sass", "less",
        "coffee", "elm", "ex", "exs", "erl", "hrl", "hs", "lhs", "clj", "cljs", "cljc", "edn",
        "scala", "sc", "groovy", "gvy", "gy", "gsh", "nim", "nims", "crystal", "cr", "d", "di",
        "pas", "pp", "inc", "dpr", "dfm", "fmx", "vb", "vbs", "vba", "bas", "cls", "frm", "ctl",
        "pag", "rep", "f", "f90", "f95", "f03", "f08", "for", "ftn", "fpp", "ada", "adb", "ads",
        "tcl", "tk", "itcl", "itk", "exp", "awk", "sed", "cmake", "make", "dockerfile", "gradle",
        "ant", "pom", "sbt", "cabal", "stack", "mix", "rebar", "cargo", "gemfile", "rakefile",
        "podfile", "fastfile", "appfile", "matchfile", "snapfile", "gymfile", "deliverfile"
    ],
    "⚙️ Executables": [
        "exe", "msi", "bat", "cmd", "jar", "apk", "appx", "ps1", "deb", "rpm", "run", "dmg", 
        "pkg", "dll", "sys", "com", "scr", "app", "ipa", "xap", "air", "bin", "bundle", "o",
        "so", "dylib", "a", "lib", "out", "elf", "mach-o", "pe", "coff", "aout", "flatpak",
        "snap", "appimage", "portable", "paf", "u3p", "vbs", "wsf", "hta", "reg", "inf",
        "cab", "msp", "mst", "msm", "gadget", "cpl", "ax", "ocx", "tsp", "drv", "efi"
    ],
    "🎨 Design": [
        "psd", "psb", "ai", "sketch", "fig", "xd", "blend", "ase", "afdesign", "afphoto", "afpub",
        "indd", "idml", "prproj", "aep", "ppj", "drw", "dwg", "dxf", "step", "stp", "iges", "igs",
        "3dm", "3ds", "max", "ma", "mb", "obj", "fbx", "dae", "ply", "stl", "x3d", "wrl", "vrml",
        "gltf", "glb", "usd", "usda", "usdc", "usdz", "c4d", "lwo", "lws", "modo", "mud", "ztl",
        "zbp", "zpr", "zsc", "rvt", "rfa", "rte", "rft", "skp", "kmz", "3mf", "amf", "cdr",
        "cmx", "vsd", "vsdx", "svg", "eps", "wmf", "emf", "cgm", "odg", "otg", "fodg"
    ],
    "🔧 Configs": [
        "ini", "cfg", "conf", "config", "env", "properties", "settings", "plist", "reg", "toml",
        "yaml", "yml", "json", "xml", "prefs", "preferences", "rc", "profile", "bashrc", "zshrc",
        "vimrc", "editorconfig", "gitconfig", "npmrc", "bowerrc", "eslintrc", "prettierrc",
        "stylelintrc", "tslint", "jsconfig", "tsconfig", "webpack", "rollup", "gulpfile",
        "gruntfile", "browserslist", "babel", "postcss", "tailwind", "next", "nuxt", "vue",
        "angular", "ember", "svelte", "astro", "vite", "parcel", "snowpack"
    ],
    "📝 Logs": [
        "log", "out", "err", "trace", "debug", "info", "warn", "error", "fatal", "access",
        "audit", "event", "syslog", "dmesg", "messages", "secure", "auth", "kern", "mail",
        "cron", "daemon", "user", "lpr", "news", "uucp", "local0", "local1", "local2", "local3",
        "local4", "local5", "local6", "local7", "wtmp", "utmp", "lastlog", "faillog", "btmp"
    ],
    "🗂️ Data": [
        "db", "sqlite", "sqlite3", "db3", "s3db", "sl3", "mdb", "accdb", "dbf", "backup", "bak",
        "sql", "dump", "bson", "avro", "parquet", "orc", "hdf5", "h5", "he5", "nc", "cdf",
        "fits", "fts", "mat", "rdata", "rds", "sas7bdat", "xpt", "dta", "sav", "por", "zsav",
        "pickle", "pkl", "joblib", "npy", "npz", "arrow", "feather", "msgpack", "protobuf",
        "pb", "tfrecord", "leveldb", "rocksdb", "berkeleydb", "gdbm", "ndbm", "dbm"
    ],
    "🔤 Fonts": [
        "ttf", "otf", "woff", "woff2", "eot", "pfb", "pfm", "afm", "fon", "fnt", "bdf", "pcf",
        "snf", "pfa", "gsf", "ttc", "otc", "dfont", "suit", "lwfn", "ffil", "cb", "vfb", "sfd",
        "ufo", "glyphs", "glyphspackage", "designspace", "fea", "kern", "mark", "mkmk", "curs",
        "liga", "rlig", "dlig", "hlig", "calt", "rclt", "clig", "ccmp", "locl", "lnum", "onum"
    ],
    "🗑️ Temporary": [
        "tmp", "temp", "cache", "crdownload", "part", "partial", "swp", "swo", "~", "bak", "old",
        "orig", "save", "autosave", "recovery", "backup", "undo", "redo", "lock", "lck", "pid",
        "thumbs", "ds_store", "spotlight-v100", "fseventsd", "temporaryitems", "trashes", "trash",
        "deleted", "recycle", "recycled", "recycler", "desktop.ini", "folder.jpg", "albumart"
    ],
    "🧪 Scientific": [
        "mat", "fig", "m", "mlx", "slx", "mdl", "sldd", "slxp", "rdata", "rds", "rda", "sas7bdat",
        "xpt", "dta", "sav", "por", "zsav", "ods", "nb", "cdf", "hdf", "hdf4", "hdf5", "h5",
        "he5", "nc", "fits", "fts", "pdb", "mol", "mol2", "sdf", "xyz", "cif", "mmcif", "pqr",
        "gro", "trr", "xtc", "edr", "tpr", "mdp", "itp", "top", "prm", "psf", "dcd", "crd",
        "rst", "ncrst", "mdcrd", "mdvel", "mden", "mdinfo", "out", "log", "com", "gjf", "inp"
    ],
    "💰 Financial": [
        "qif", "ofx", "qfx", "iif", "csv", "qbo", "qbw", "qbb", "qbm", "qbx", "qby", "qbz",
        "tax", "taxreturn", "xlsx", "xls", "pdf", "p7s", "p7m", "p7c", "p7b", "cer", "crt",
        "der", "pem", "pfx", "p12", "jks", "keystore", "truststore", "cacerts"
    ],
    "🏥 Medical": [
        "dcm", "dicom", "nii", "nii.gz", "img", "hdr", "analyze", "minc", "mnc", "mgz", "mgh",
        "nrrd", "nhdr", "vtk", "vti", "vtp", "vtu", "vtr", "vts", "pvti", "pvtp", "pvtu",
        "pvtr", "pvts", "mhd", "mha", "gipl", "hl7", "cda", "ccda", "fhir", "json", "xml"
    ],
    "🌍 GIS": [
        "shp", "shx", "dbf", "prj", "cpg", "qix", "fix", "kml", "kmz", "gpx", "tcx", "fit",
        "geojson", "topojson", "gml", "gdb", "mdb", "e00", "000", "adf", "tif", "tiff", "img",
        "ecw", "sid", "jp2", "mrsid", "dt0", "dt1", "dt2", "hgt", "bil", "hdr", "blw", "prj",
        "aux", "ovr", "rrd", "pyramid", "rsc", "tab", "map", "id", "dat", "ind", "wor", "style"
    ],
    "🎭 CAD": [
        "dwg", "dxf", "dwf", "dwt", "dws", "dxb", "sat", "3dm", "igs", "iges", "step", "stp",
        "x_t", "x_b", "xmt_txt", "xmt_bin", "prt", "asm", "par", "psm", "pwd", "sldprt", "sldasm",
        "slddrw", "catpart", "catproduct", "catdrawing", "cgr", "session", "exp", "dlv", "model",
        "drw", "neu", "prt", "asm", "frm", "mf1", "pkg", "unv", "ipt", "iam", "idw", "ipn"
    ],
    "🔐 Encryption": [
        "gpg", "pgp", "asc", "sig", "p7s", "p7m", "p7c", "p7b", "cer", "crt", "der", "pem",
        "pfx", "p12", "jks", "keystore", "truststore", "cacerts", "key", "pub", "sec", "skr",
        "pkr", "axx", "cpt", "sea", "hqx", "sit", "sitx", "encrypted", "enc", "cipher", "crypt",
        "protected", "secure", "locked", "vault", "safe", "kdb", "kdbx", "1password", "lastpass"
    ],
    "📱 Mobile": [
        "apk", "aab", "ipa", "app", "appx", "appxbundle", "msix", "msixbundle", "xap", "air",
        "ane", "swc", "swf", "fla", "as", "mxml", "flex", "actionscript", "dex", "odex", "vdex",
        "art", "oat", "pro", "r8", "mapping", "proguard", "symbols", "dsym", "plist", "entitlements",
        "mobileprovision", "p8", "p12", "cer", "csr", "certSigningRequest", "developerprofile"
    ],
    "🌐 Web": [
        "html", "htm", "xhtml", "xml", "xsl", "xslt", "dtd", "xsd", "css", "scss", "sass", "less",
        "styl", "js", "mjs", "jsx", "ts", "tsx", "coffee", "dart", "elm", "vue", "svelte", "astro",
        "php", "asp", "aspx", "jsp", "jsp", "erb", "ejs", "hbs", "handlebars", "mustache", "twig",
        "blade", "liquid", "njk", "nunjucks", "pug", "jade", "haml", "slim", "eco", "dust", "soy",
        "wasm", "wat", "map", "manifest", "appcache", "webmanifest", "browserconfig", "humans",
        "robots", "sitemap", "rss", "atom", "feed", "opml", "vcard", "vcf", "ics", "ical"
    ],
    "❓ Misc": []  # Fallback category
}

def format_bytes(bytes_value: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    log_dir = Path.home() / ".autocleaner" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"autocleaner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger('AutoClean')
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger

class EnhancedAutoClean:
    """Enhanced AutoClean with better UX, performance, and features"""
    
    def __init__(self, 
                 folder_paths: List[str], 
                 dry_run: bool = False,
                 auto_organize: bool = False,
                 create_backup: bool = True,
                 delete_empty: bool = False,
                 log_level: str = "INFO"):
        
        self.folder_paths = [Path(path).resolve() for path in folder_paths]
        self.dry_run = dry_run
        self.auto_organize = auto_organize
        self.create_backup = create_backup
        self.delete_empty = delete_empty
        self.logger = setup_logging(log_level)
        
        # Data storage
        self.files_data: Dict[str, List[FileInfo]] = defaultdict(list)
        self.categorized_files: Dict[str, Dict[str, List[FileInfo]]] = defaultdict(lambda: defaultdict(list))
        self.results: List[OrganizationResult] = []
        
        # Validate paths
        self._validate_paths()
        
    def _validate_paths(self):
        """Validate that all provided paths exist"""
        invalid_paths = [p for p in self.folder_paths if not p.exists()]
        if invalid_paths:
            console.print(f"[bold red]Error:[/bold red] The following paths don't exist:")
            for path in invalid_paths:
                console.print(f"  • {path}")
            sys.exit(1)
    
    def scan_files(self) -> Dict[str, List[FileInfo]]:
        """Scan all files in the provided directories"""
        console.print("[bold blue]🔍 Scanning files...[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
            transient=True
        ) as progress:
            
            for folder_path in self.folder_paths:
                folder_str = str(folder_path)
                task = progress.add_task(f"Scanning {folder_path.name}...", total=None)
                
                try:
                    files = [f for f in folder_path.iterdir() if f.is_file()]
                    progress.update(task, total=len(files))
                    
                    for file_path in files:
                        try:
                            file_info = FileInfo.from_path(file_path)
                            self.files_data[folder_str].append(file_info)
                            progress.advance(task)
                        except (OSError, PermissionError) as e:
                            self.logger.warning(f"Could not access file {file_path}: {e}")
                            continue
                            
                except (OSError, PermissionError) as e:
                    self.logger.error(f"Could not access directory {folder_path}: {e}")
                    continue
        
        total_files = sum(len(files) for files in self.files_data.values())
        console.print(f"[green]✅ Found {total_files} files across {len(self.folder_paths)} directories[/green]")
        
        return self.files_data

    def categorize_files(self) -> Dict[str, Dict[str, List[FileInfo]]]:
        """Categorize files based on their extensions"""
        console.print("[bold blue]📂 Categorizing files...[/bold blue]")
        
        ambiguous_files = defaultdict(list)
        
        for folder_path, files in self.files_data.items():
            for file_info in files:
                matching_categories = []
                
                # Find all matching categories
                for category, extensions in FILE_CATEGORIES.items():
                    if file_info.extension in extensions:
                        matching_categories.append(category)
                
                if len(matching_categories) == 1:
                    # Single match - auto-categorize
                    file_info.category = matching_categories[0]
                    self.categorized_files[folder_path][matching_categories[0]].append(file_info)
                elif len(matching_categories) > 1:
                    # Multiple matches - need user input
                    ambiguous_files[folder_path].append((file_info, matching_categories))
                else:
                    # No matches - put in Misc
                    file_info.category = "❓ Misc"
                    self.categorized_files[folder_path]["❓ Misc"].append(file_info)
        
        # Handle ambiguous files
        if ambiguous_files and not self.auto_organize:
            self._resolve_ambiguous_files(ambiguous_files)
        elif ambiguous_files and self.auto_organize:
            self._auto_resolve_ambiguous_files(ambiguous_files)
        
        return self.categorized_files

    def _resolve_ambiguous_files(self, ambiguous_files: Dict[str, List[Tuple[FileInfo, List[str]]]]):
        """Interactively resolve files that match multiple categories"""
        console.print("[bold yellow]🤔 Some files match multiple categories. Please choose:[/bold yellow]")
        
        custom_style = Style([
            ('qmark', 'fg:#ff9d00 bold'),
            ('question', 'bold'),
            ('answer', 'fg:#ff9d00 bold'),
            ('pointer', 'fg:#ff9d00 bold'),
            ('highlighted', 'fg:#ff9d00 bold'),
            ('selected', 'fg:#cc5454'),
            ('separator', 'fg:#cc5454'),
            ('instruction', ''),
            ('text', ''),
            ('disabled', 'fg:#858585 italic')
        ])
        
        for folder_path, ambiguous_list in ambiguous_files.items():
            console.print(f"\n[bold cyan]📁 {Path(folder_path).name}[/bold cyan]")
            
            for file_info, categories in ambiguous_list:
                choice = questionary.select(
                    f"📄 {file_info.name} ({file_info.size_human}) matches multiple categories:",
                    choices=categories + ["❓ Misc", "⏭️ Skip this file"],
                    style=custom_style
                ).ask()
                
                if choice and choice != "⏭️ Skip this file":
                    file_info.category = choice
                    self.categorized_files[folder_path][choice].append(file_info)

    def _auto_resolve_ambiguous_files(self, ambiguous_files: Dict[str, List[Tuple[FileInfo, List[str]]]]):
        """Automatically resolve ambiguous files by picking the first match"""
        for folder_path, ambiguous_list in ambiguous_files.items():
            for file_info, categories in ambiguous_list:
                x = random.randint(0, 1)
                if x >= 1:
                    chosen_category = categories[0]  # Pick first match
                else:
                    chosen_category = random.choice(categories) # Pick random one
                file_info.category = chosen_category
                self.categorized_files[folder_path][chosen_category].append(file_info)
                self.logger.info(f"Auto-resolved {file_info.name} to category {chosen_category}")

    def display_organization_preview(self):
        """Display a preview of the planned organization"""
        console.print("\n[bold blue]📋 Organization Preview[/bold blue]")
        
        for folder_path, categories in self.categorized_files.items():
            folder_name = Path(folder_path).name
            
            # Create a tree view
            tree = Tree(f"📁 [bold cyan]{folder_name}[/bold cyan]")
            
            total_files = 0
            total_size = 0
            
            for category, files in categories.items():
                if not files:
                    continue
                    
                category_size = sum(f.size_bytes for f in files)
                category_node = tree.add(
                    f"{category} ([green]{len(files)} files[/green], [blue]{format_bytes(category_size)}[/blue])"
                )
                
                # Show a few example files
                for file_info in files[:3]:
                    category_node.add(f"📄 {file_info.name} ({file_info.size_human})")
                
                if len(files) > 3:
                    category_node.add(f"... and {len(files) - 3} more files")
                
                total_files += len(files)
                total_size += category_size
            
            tree.add(f"[bold]Total: {total_files} files, {format_bytes(total_size)}[/bold]")
            console.print(tree)

    def organize_files(self):
        """Organize files into category folders"""
        if not self.categorized_files:
            console.print("[yellow]⚠️ No files to organize[/yellow]")
            return
        
        start_time = time.time()
        
        # Show preview first
        self.display_organization_preview()
        
        if not self.dry_run and not self.auto_organize:
            if not Confirm.ask("\n[bold]Proceed with organization?[/bold]"):
                console.print("[yellow]Operation cancelled[/yellow]")
                return
        
        if self.dry_run:
            console.print("\n[bold yellow]🔍 DRY RUN MODE - No files will be moved[/bold yellow]")
        else:
            console.print("\n[bold green]🚀 Starting file organization...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            for folder_path, categories in self.categorized_files.items():
                base_path = Path(folder_path)
                
                # Calculate total files for this folder
                total_files = sum(len(files) for files in categories.values())
                task = progress.add_task(f"Organizing {base_path.name}...", total=total_files)
                
                organized_files = 0
                skipped_files = 0
                categories_created = []
                files_by_category = defaultdict(list)
                
                for category, files in categories.items():
                    if not files:
                        continue
                    
                    # Create category folder
                    category_folder = base_path / category.split()[-1]  # Remove emoji for folder name
                    
                    if not self.dry_run:
                        category_folder.mkdir(exist_ok=True)
                        if category not in categories_created:
                            categories_created.append(category)
                    
                    # Move files
                    for file_info in files:
                        try:
                            source_path = Path(file_info.full_path)
                            dest_path = category_folder / file_info.name
                            
                            if not self.dry_run:
                                if dest_path.exists():
                                    # Handle duplicates by adding timestamp
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    stem = dest_path.stem
                                    suffix = dest_path.suffix
                                    dest_path = category_folder / f"{stem}_{timestamp}{suffix}"
                                
                                shutil.move(str(source_path), str(dest_path))
                                file_info.full_path = str(dest_path)
                            
                            files_by_category[category].append(file_info)
                            organized_files += 1
                            
                        except Exception as e:
                            self.logger.error(f"Failed to move {file_info.name}: {e}")
                            skipped_files += 1
                        
                        progress.advance(task)
                
                # Store results
                processing_time = time.time() - start_time
                result = OrganizationResult(
                    total_files=total_files,
                    organized_files=organized_files,
                    skipped_files=skipped_files,
                    categories_created=categories_created,
                    total_size=sum(f.size_bytes for files in files_by_category.values() for f in files),
                    processing_time=processing_time,
                    files_by_category=dict(files_by_category)
                )
                self.results.append(result)

    def generate_report(self):
        """Generate a detailed organization report"""
        if not self.results:
            return
        
        console.print("\n[bold blue]📊 Organization Report[/bold blue]")
        
        # Summary table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        total_files = sum(r.total_files for r in self.results)
        total_organized = sum(r.organized_files for r in self.results)
        total_skipped = sum(r.skipped_files for r in self.results)
        total_size = sum(r.total_size for r in self.results)
        avg_processing_time = sum(r.processing_time for r in self.results) / len(self.results)
        
        table.add_row("Total Files Processed", str(total_files))
        table.add_row("Files Organized", str(total_organized))
        table.add_row("Files Skipped", str(total_skipped))
        table.add_row("Total Size Organized", format_bytes(total_size))
        table.add_row("Success Rate", f"{(total_organized/total_files)*100:.1f}%" if total_files > 0 else "0%")
        table.add_row("Average Processing Time", f"{avg_processing_time:.2f}s")
        
        console.print(table)
        
        # Category breakdown
        if self.results:
            console.print("\n[bold blue]📁 Category Breakdown[/bold blue]")
            
            all_categories = Counter()
            for result in self.results:
                for category, files in result.files_by_category.items():
                    all_categories[category] += len(files)
            
            category_table = Table(show_header=True, header_style="bold magenta")
            category_table.add_column("Category", style="cyan")
            category_table.add_column("Files", style="green", justify="right")
            category_table.add_column("Percentage", style="yellow", justify="right")
            
            for category, count in all_categories.most_common():
                percentage = (count / total_organized) * 100 if total_organized > 0 else 0
                category_table.add_row(category, str(count), f"{percentage:.1f}%")
            
            console.print(category_table)

    def save_report(self, output_path: Optional[str] = None):
        """Save organization report to JSON file"""
        if not self.results:
            return
        
        if output_path is None:
            report_dir = Path.home() / ".autocleaner" / "reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            output_path = report_dir / f"organization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "folder_paths": [str(p) for p in self.folder_paths],
            "settings": {
                "dry_run": self.dry_run,
                "auto_organize": self.auto_organize,
                "create_backup": self.create_backup,
                "delete_empty": self.delete_empty
            },
            "results": [asdict(result) for result in self.results]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]💾 Report saved to: {output_path}[/green]")

    def cleanup_empty_folders(self):
        """Remove empty folders after organization"""
        if not self.delete_empty:
            return
        
        console.print("[bold blue]🧹 Cleaning up empty folders...[/bold blue]")
        
        removed_count = 0
        for folder_path in self.folder_paths:
            for root, dirs, files in os.walk(folder_path, topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        if not any(dir_path.iterdir()):  # Empty directory
                            if not self.dry_run:
                                dir_path.rmdir()
                            removed_count += 1
                            self.logger.info(f"Removed empty directory: {dir_path}")
                    except OSError:
                        continue
        
        if removed_count > 0:
            console.print(f"[green]✅ Removed {removed_count} empty folders[/green]")

    def run(self):
        """Main execution method"""
        try:
            console.print(Panel.fit(
                "[bold blue]🚀 Enhanced AutoClean File Organizer[/bold blue]\n"
                f"Mode: {'🔍 DRY RUN' if self.dry_run else '🔄 LIVE'}\n"
                f"Auto-organize: {'✅' if self.auto_organize else '❌'}\n"
                f"Folders: {len(self.folder_paths)}",
                border_style="blue"
            ))
            
            # Step 1: Scan files
            self.scan_files()
            
            # Step 2: Categorize files
            self.categorize_files()
            
            # Step 3: Organize files
            self.organize_files()
            
            # Step 4: Generate report
            self.generate_report()
            
            # Step 5: Save report
            self.save_report()
            
            # Step 6: Cleanup empty folders
            self.cleanup_empty_folders()
            
            console.print("\n[bold green]🎉 Organization complete![/bold green]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Operation cancelled by user[/yellow]")
        except Exception as e:
            console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
            self.logger.error(f"Unexpected error: {e}", exc_info=True)

def get_common_folders():
    """Get common folders that users typically want to organize"""
    home = Path.home()
    common_folders = {
        'downloads': home / 'Downloads',
        'desktop': home / 'Desktop', 
        'documents': home / 'Documents',
        'pictures': home / 'Pictures',
        'videos': home / 'Videos',
        'music': home / 'Music'
    }
    
    # Return only existing folders
    return {name: path for name, path in common_folders.items() if path.exists()}

def interactive_folder_selection():
    """Interactive folder selection if no folders provided"""
    common_folders = get_common_folders()
    
    if not common_folders:
        console.print("[red]❌ No common folders found. Please specify folders manually.[/red]")
        return []
    
    console.print("[bold blue]📁 Select folders to organize:[/bold blue]")
    
    choices = []
    for name, path in common_folders.items():
        file_count = len([f for f in path.iterdir() if f.is_file()]) if path.exists() else 0
        choices.append({
            'name': f"{name.title()} ({path}) - {file_count} files",
            'value': str(path)
        })
    
    choices.append({'name': "Other (specify manually)", 'value': 'other'})
    
    try:
        import questionary
        selected = questionary.checkbox(
            "Choose folders:",
            choices=choices
        ).ask()
        
        if not selected:
            return []
        
        folders = []
        for selection in selected:
            if selection == 'other':
                custom_path = questionary.text("Enter folder path:").ask()
                if custom_path:
                    folders.append(custom_path)
            else:
                folders.append(selection)
        
        return folders
    except ImportError:
        # Fallback if questionary not available
        console.print("Available folders:")
        for i, (name, path) in enumerate(common_folders.items(), 1):
            file_count = len([f for f in path.iterdir() if f.is_file()]) if path.exists() else 0
            console.print(f"  {i}. {name.title()} ({path}) - {file_count} files")
        
        return [str(common_folders['downloads'])] if 'downloads' in common_folders else []

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced AutoClean File Organizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive folder selection
  %(prog)s ~/Downloads               # Organize Downloads folder
  %(prog)s ~/Downloads ~/Desktop --dry-run
  %(prog)s ~/Downloads --auto-organize --delete-empty
  %(prog)s downloads                 # Use shorthand for common folders
        """
    )
    
    parser.add_argument(
        "folders",
        nargs="*",  # Changed from "+" to "*" to make it optional
        help="Folders to organize (or use shortcuts: downloads, desktop, documents, pictures, videos, music)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without actually moving files"
    )
    
    parser.add_argument(
        "--auto-organize",
        action="store_true",
        help="Automatically resolve ambiguous files without user input"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup archives"
    )
    
    parser.add_argument(
        "--delete-empty",
        action="store_true",
        help="Delete empty folders after organization"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level"
    )
    
    args = parser.parse_args()
    
    # Handle folder selection
    folders = args.folders
    
    if not folders:
        # Interactive selection if no folders provided
        folders = interactive_folder_selection()
        if not folders:
            console.print("[yellow]⚠️ No folders selected. Exiting.[/yellow]")
            return
    
    # Handle common folder shortcuts
    common_folders = get_common_folders()
    resolved_folders = []
    
    for folder in folders:
        folder_lower = folder.lower()
        if folder_lower in common_folders:
            resolved_folders.append(str(common_folders[folder_lower]))
            console.print(f"[green]✅ Using {folder_lower}: {common_folders[folder_lower]}[/green]")
        else:
            resolved_folders.append(folder)
    
    # Create and run organizer
    organizer = EnhancedAutoClean(
        folder_paths=resolved_folders,
        dry_run=args.dry_run,
        auto_organize=args.auto_organize,
        create_backup=not args.no_backup,
        delete_empty=args.delete_empty,
        log_level=args.log_level
    )
    
    organizer.run()

if __name__ == "__main__":
    main()