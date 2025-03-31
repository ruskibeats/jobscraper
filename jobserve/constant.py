# Constants for JobServe scraper

# Base URL for the job site
BASE_URL = "https://www.jobserve.com"

# Search URL for job listings
SEARCH_URL = f"{BASE_URL}/gb/en/JobSearch.aspx"

# Headers for HTTP requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# CSS selectors for job elements
SELECTORS = {
    "job_card": "div.jobListItem",
    "job_title": "h2.jobListItemTitle",
    "company_name": "div.jobListItemCompany",
    "job_location": "div.jobListItemLocation",
    "job_type": "div.jobListItemType",
    "job_date": "div.jobListItemDate",
    "job_salary": "div.jobListItemSalary",
    "job_description": "div.jobListItemDescription",
}

# Job type mappings
JOB_TYPE_MAPPINGS = {
    "permanent": "fulltime",
    "full time": "fulltime",
    "part time": "parttime",
    "contract": "contract",
    "temporary": "temporary",
    "internship": "internship",
    "freelance": "contract",
}

# Currency mappings
CURRENCY_MAPPINGS = {
    "£": "GBP",
    "$": "USD",
    "€": "EUR",
    "¥": "JPY",
    "₹": "INR",
    "A$": "AUD",
    "C$": "CAD",
}

# Country mappings
COUNTRY_MAPPINGS = {
    "uk": "United Kingdom",
    "gb": "United Kingdom",
    "us": "United States",
    "ca": "Canada",
    "au": "Australia",
    "de": "Germany",
    "fr": "France",
    "es": "Spain",
    "it": "Italy",
    "nl": "Netherlands",
    "be": "Belgium",
    "ch": "Switzerland",
    "at": "Austria",
    "se": "Sweden",
    "dk": "Denmark",
    "no": "Norway",
    "fi": "Finland",
    "ie": "Ireland",
    "pt": "Portugal",
    "gr": "Greece",
    "pl": "Poland",
    "cz": "Czech Republic",
    "hu": "Hungary",
    "ro": "Romania",
    "bg": "Bulgaria",
    "hr": "Croatia",
    "si": "Slovenia",
    "sk": "Slovakia",
    "ee": "Estonia",
    "lv": "Latvia",
    "lt": "Lithuania",
    "cy": "Cyprus",
    "mt": "Malta",
    "lu": "Luxembourg",
    "is": "Iceland",
    "li": "Liechtenstein",
    "mc": "Monaco",
    "sm": "San Marino",
    "va": "Vatican City",
    "ad": "Andorra",
    "jp": "Japan",
    "cn": "China",
    "in": "India",
    "sg": "Singapore",
    "hk": "Hong Kong",
    "my": "Malaysia",
    "th": "Thailand",
    "id": "Indonesia",
    "ph": "Philippines",
    "vn": "Vietnam",
    "kr": "South Korea",
    "tw": "Taiwan",
    "nz": "New Zealand",
    "za": "South Africa",
    "br": "Brazil",
    "mx": "Mexico",
    "ar": "Argentina",
    "cl": "Chile",
    "co": "Colombia",
    "pe": "Peru",
    "ve": "Venezuela",
    "ae": "United Arab Emirates",
    "sa": "Saudi Arabia",
    "qa": "Qatar",
    "kw": "Kuwait",
    "bh": "Bahrain",
    "om": "Oman",
    "il": "Israel",
    "tr": "Turkey",
    "eg": "Egypt",
    "ma": "Morocco",
    "ng": "Nigeria",
    "ke": "Kenya",
    "gh": "Ghana",
    "za": "South Africa",
}
