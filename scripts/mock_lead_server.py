import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

LEADS = [
    {
        "first_name": "John",
        "last_name": "Smith",
        "job_title": "Chief Technology Officer",
        "email": "john.smith@techvision.com",
        "company_name": "TechVision Solutions",
        "domain": "techvision.com",
        "industry": "Software",
        "country": "United States",
        "employee_count": 250,
    },
    {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "job_title": "Head of Marketing",
        "email": "sarah.johnson@cloudworks.com",
        "company_name": "CloudWorks Inc",
        "domain": "cloudworks.com",
        "industry": "Cloud Computing",
        "country": "United States",
        "employee_count": 500,
    },
    {
        "first_name": "Michael",
        "last_name": "Brown",
        "job_title": "Chief Executive Officer",
        "email": "michael.brown@datacore.io",
        "company_name": "DataCore Analytics",
        "domain": "datacore.io",
        "industry": "Data Analytics",
        "country": "United Kingdom",
        "employee_count": 120,
    },
    {
        "first_name": "Emily",
        "last_name": "Davis",
        "job_title": "Chief Financial Officer",
        "email": "emily.davis@fintechpro.com",
        "company_name": "FinTech Pro",
        "domain": "fintechpro.com",
        "industry": "Financial Technology",
        "country": "United States",
        "employee_count": 350,
    },
    {
        "first_name": "Daniel",
        "last_name": "Wilson",
        "job_title": "VP of Engineering",
        "email": "daniel.wilson@innovatelabs.ai",
        "company_name": "Innovate Labs",
        "domain": "innovatelabs.ai",
        "industry": "Artificial Intelligence",
        "country": "Canada",
        "employee_count": 180,
    },
    {
        "first_name": "Olivia",
        "last_name": "Taylor",
        "job_title": "Director of Sales",
        "email": "olivia.taylor@growthhub.com",
        "company_name": "GrowthHub",
        "domain": "growthhub.com",
        "industry": "Marketing Technology",
        "country": "United States",
        "employee_count": 75,
    },
    {
        "first_name": "James",
        "last_name": "Anderson",
        "job_title": "Chief Operating Officer",
        "email": "james.anderson@enterprisesync.com",
        "company_name": "EnterpriseSync",
        "domain": "enterprisesync.com",
        "industry": "Enterprise Software",
        "country": "Germany",
        "employee_count": 800,
    },
    {
        "first_name": "Sophia",
        "last_name": "Thomas",
        "job_title": "Product Manager",
        "email": "sophia.thomas@productforge.com",
        "company_name": "ProductForge",
        "domain": "productforge.com",
        "industry": "Software",
        "country": "Australia",
        "employee_count": 95,
    },
    {
        "first_name": "William",
        "last_name": "Jackson",
        "job_title": "Chief Information Officer",
        "email": "william.jackson@securedata.io",
        "company_name": "SecureData",
        "domain": "securedata.io",
        "industry": "Cybersecurity",
        "country": "United States",
        "employee_count": 420,
    },
    {
        "first_name": "Ava",
        "last_name": "White",
        "job_title": "Business Development Director",
        "email": "ava.white@marketbridge.com",
        "company_name": "MarketBridge",
        "domain": "marketbridge.com",
        "industry": "Business Services",
        "country": "Canada",
        "employee_count": 210,
    },
    {
        "first_name": "Alexander",
        "last_name": "Harris",
        "job_title": "Chief Technology Officer",
        "email": "alexander.harris@softmatrix.com",
        "company_name": "SoftMatrix",
        "domain": "softmatrix.com",
        "industry": "Software",
        "country": "United States",
        "employee_count": 600,
    },
    {
        "first_name": "Mia",
        "last_name": "Martin",
        "job_title": "VP of Marketing",
        "email": "mia.martin@brandlogic.com",
        "company_name": "BrandLogic",
        "domain": "brandlogic.com",
        "industry": "Marketing",
        "country": "United Kingdom",
        "employee_count": 140,
    },
]

REQUEST_COUNTS = {}


def render_lead(lead):
    return f"""
    <div class="lead-card">
        <h2 class="person-name">
            {html.escape(lead["first_name"])}
            {html.escape(lead["last_name"])}
        </h2>

        <p class="job-title">
            {html.escape(lead["job_title"])}
        </p>

        <p class="email">
            {html.escape(lead["email"])}
        </p>

        <div class="company">
            <span class="company-name">
                {html.escape(lead["company_name"])}
            </span>

            <span class="domain">
                {html.escape(lead["domain"])}
            </span>

            <span class="industry">
                {html.escape(lead["industry"])}
            </span>

            <span class="country">
                {html.escape(lead["country"])}
            </span>

            <span class="employee-count">
                {lead["employee_count"]}
            </span>
        </div>
    </div>
    """


class LeadDirectoryHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)

        REQUEST_COUNTS[parsed_url.path] = (
            REQUEST_COUNTS.get(
                parsed_url.path,
                0,
            )
            + 1
        )

        if parsed_url.path != "/leads":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Page not found")
            return

        query = parse_qs(parsed_url.query)

        try:
            page = int(
                query.get(
                    "page",
                    ["1"],
                )[0]
            )
        except ValueError:
            page = 1

        request_key = f"/leads?page={page}"

        REQUEST_COUNTS[request_key] = (
            REQUEST_COUNTS.get(
                request_key,
                0,
            )
            + 1
        )

        if page == 2 and REQUEST_COUNTS[request_key] <= 2:
            print("[SERVER] Simulating temporary failure for page 2")

            self.send_response(503)
            self.send_header(
                "Content-Type",
                "text/plain",
            )
            self.end_headers()

            self.wfile.write(b"Temporary server failure")

            return

        leads_per_page = 4

        start = (page - 1) * leads_per_page
        end = start + leads_per_page

        page_leads = LEADS[start:end]

        total_pages = (len(LEADS) + leads_per_page - 1) // leads_per_page

        lead_html = ""

        for lead in page_leads:
            lead_html += render_lead(lead)

        next_page = page + 1 if page < total_pages else None
        previous_page = page - 1 if page > 1 else None

        next_link = (
            f'<a class="next-page" href="/leads?page={next_page}">Next</a>'
            if next_page
            else ""
        )

        previous_link = (
            f'<a class="previous-page" href="/leads?page={previous_page}">Previous</a>'
            if previous_page
            else ""
        )

        page_html = f"""
        <!DOCTYPE html>

        <html>
        <head>
            <title>B2B Lead Directory - Page {page}</title>

            <meta charset="UTF-8">

            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 1000px;
                    margin: 40px auto;
                    padding: 20px;
                }}

                .lead-card {{
                    border: 1px solid #ddd;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                }}

                .person-name {{
                    margin-bottom: 5px;
                }}

                .job-title {{
                    font-weight: bold;
                }}

                .email {{
                    color: #333;
                }}

                .company {{
                    display: flex;
                    gap: 20px;
                    flex-wrap: wrap;
                    margin-top: 15px;
                }}

                .pagination {{
                    margin-top: 30px;
                    display: flex;
                    justify-content: space-between;
                }}

                a {{
                    text-decoration: none;
                    font-weight: bold;
                }}
            </style>
        </head>

        <body>

            <h1>B2B Lead Directory</h1>

            <p class="page-number">
                Page {page} of {total_pages}
            </p>

            <section class="lead-list">
                {lead_html}
            </section>

            <nav class="pagination">
                {previous_link}
                {next_link}
            </nav>

        </body>

        </html>
        """

        response = page_html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()

        self.wfile.write(response)

    def log_message(self, format, *args):
        print(f"[SERVER] {format % args}")


def run_server():
    host = "127.0.0.1"
    port = 8000

    server = HTTPServer(
        (host, port),
        LeadDirectoryHandler,
    )

    print("=" * 60)
    print("B2B Lead Directory Server")
    print("=" * 60)
    print(f"Server running at: http://{host}:{port}")
    print(f"Lead directory:    http://{host}:{port}/leads?page=1")
    print("Press CTRL+C to stop the server.")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()