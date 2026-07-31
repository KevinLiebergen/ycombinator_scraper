import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.job_parser import parse_job_details

CASES = [
    # (title, expected_role, expected_location)
    ("Tasklet (YC P26) Is Hiring a Customer Success Engineer",
     "Customer Success Engineer", None),
    ("Rise Reforming (YC S26) Is Hiring",
     None, None),
    ("Mbodi AI (YC P25) Is Hiring Robotics/Research Engineers",
     "Robotics/Research Engineers", None),
    ("SalesPatriot (YC W25) Is Hiring Full Stack Engineers (SF)",
     "Full Stack Engineers", "SF"),
    ("Kontigo (YC S24) Is Hiring (Head of Security)",
     "Head of Security", None),
    ("UpCodes (YC S17) is hiring remote AE's to help make buildings cheaper",
     "AE's", "Remote"),
    ("Manufact (YC S25) Is Hiring a Senior infra engineer to build the MCP cloud",
     "Senior infra engineer", None),
    ("9 Mothers (YC P26) Is Hiring in Austin, TX",
     None, "Austin, TX"),
    ("Stealth robotics startup (YC S26) is hiring principal engineers (Palo Alto)",
     "principal engineers", "Palo Alto"),
    ("TrueBiz (YC S22) – Senior Software Engineer – Remote (US) – Full-Time",
     "Senior Software Engineer", "Remote (US)"),
    ("Lago (YC S21) Is Hiring for Our GTM Team",
     "GTM Team", None),
    ("Bloomy (YC S26) is hiring a founding engineer",
     "founding engineer", None),
    ("Acme (YC W20) is hiring a Backend Engineer in San Francisco",
     "Backend Engineer", "San Francisco"),
    ("Acme (YC W20) is hiring a Data Scientist (Remote)",
     "Data Scientist", "Remote"),
    ("Hive (YC S14) is hiring sr back-end developers (CA/US remote OK)",
     "sr back-end developers", "CA/US remote OK"),
    ("Flexport (YC W14) Is Hiring in Indonesia, India, and Thailand",
     None, "Indonesia, India, and Thailand"),
    ("Ashby (YC W19) Is Hiring EMEA Engineers Who Can Design",
     "EMEA Engineers Who Can Design", None),
    ("Charge Robotics (YC S21) Is Hiring Software and Hardware Engineers",
     "Software and Hardware Engineers", None),
]

failures = []
for title, expected_role, expected_location in CASES:
    role, location = parse_job_details(title)
    if (role, location) != (expected_role, expected_location):
        failures.append(
            f"  {title!r}\n    expected role={expected_role!r} location={expected_location!r}\n"
            f"    got      role={role!r} location={location!r}"
        )
    else:
        print(f"OK  role={role!r:35} location={location!r:18} <- {title}")

# Must never raise on odd input.
for weird in [None, "", "   ", "(YC S24)", "No YC tag here", "Company (YC S24)"]:
    parse_job_details(weird)

if failures:
    print("\nFAILURES:\n" + "\n".join(failures))
    sys.exit(1)

print("\nSUCCESS: job title parsing works as expected.")
