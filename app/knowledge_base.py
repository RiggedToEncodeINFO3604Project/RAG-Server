from dataclasses import dataclass, field

# Knowledge Base Sections
@dataclass(frozen=True)
class Section:
    id:       str
    title:    str
    keywords: list[str] = field(default_factory=list)
    content:  str       = ""


SECTIONS: list[Section] = [
    Section(
        id="overview",
        title="1. General Product Overview",
        keywords=[
            "skedulelt", "skeduleit", "what is", "about", "overview",
            "platform", "ios", "android", "trinidad", "mobile app",
            "website", "web app",
        ],
        content=(
            "SkeduleIt is a mobile scheduling and payment solution designed for service\n"
            "providers and customers in Trinidad & Tobago (T&T).\n"
            "\n"
            "Target Users : Service businesses (barbers, hairdressers, aestheticians, etc.)\n"
            "               and their customers.\n"
            "Platforms    : iOS and Android mobile apps, plus a public website.\n"
            "               A web app with full functionality will be available soon.\n"
            "\n"
            "Two Apps:\n"
            "• Customer App  - Browse businesses, book appointments, manage bookings\n"
            "• Business App  - Manage profile, services, team, availability, payments"
        ),
    ),
    
    Section(
        id="account_signup",
        title="2. Account Creation & Signup",
        keywords=[
            "sign up", "signup", "create account", "register", "new account",
            "customer account", "business account", "credit card", "payment info",
            "approval", "review process", "free trial",
        ],
        content=(
            "=== Customer Accounts ===\n"
            "When you create a customer account, you can immediately:\n"
            "• Browse businesses\n"
            "• Schedule appointments\n"
            "• Manage upcoming appointments\n"
            "• Receive confirmations and reminders\n"
            "\n"
            "No credit card required. Your account is active immediately upon signup.\n"
            "\n"
            "=== Business Accounts ===\n"
            "When a business signs up, the account enters a brief review process to ensure\n"
            "only legitimate businesses are listed. Once approved, you can:\n"
            "• Create your business profile\n"
            "• Add services and pricing\n"
            "• Add team members (service providers)\n"
            "• Manage availability\n"
            "• Handle appointments\n"
            "• Use payment and reporting tools\n"
            "\n"
            "No credit card required during signup or free trial. Payment details are only\n"
            "needed if you choose to continue with a paid plan after the trial.\n"
            "\n"
            "=== Guest Booking ===\n"
            "Customers can browse and book appointments WITHOUT creating an account, but\n"
            "certain features (like managing bookings and receiving reminders) require signup."
        ),
    ),
    
    Section(
        id="business_vs_provider",
        title="3. Business vs Service Provider",
        keywords=[
            "business", "service provider", "team member", "employee",
            "sole trader", "independent contractor", "difference",
            "multiple providers", "add team", "staff",
        ],
        content=(
            "=== What's the Difference? ===\n"
            "\n"
            "Business:\n"
            "The company or entity listed on SkeduleIt (e.g., 'Trini Cuts Barbershop').\n"
            "\n"
            "Service Provider:\n"
            "An individual who performs the service - whether an employee, team member,\n"
            "sole trader, or independent contractor under that business.\n"
            "\n"
            "Example:\n"
            "• 'Trini Cuts Barbershop' is the Business\n"
            "• 'Marcus (Barber)' and 'Jade (Barber)' are Service Providers\n"
            "\n"
            "For Sole Traders:\n"
            "If you work alone, the business and service provider are essentially the same.\n"
            "\n"
            "=== Adding Multiple Service Providers ===\n"
            "Yes! Businesses can add multiple service providers or team members to their\n"
            "account and assign specific services to each person."
        ),
    ),
    
    Section(
        id="customer_faq",
        title="4. Customer FAQ",
        keywords=[
            "book", "booking", "schedule", "appointment", "make appointment",
            "browse", "search", "find business", "cancel appointment",
            "manage booking", "confirmation", "reminder",
        ],
        content=(
            "=== How do I book an appointment? ===\n"
            "Open the SkeduleIt Customer App, browse or search for a business, view their\n"
            "services and availability, and select a time slot. You can book with or without\n"
            "creating an account.\n"
            "\n"
            "=== Can I manage my appointments? ===\n"
            "Yes! If you have a customer account, you can view, reschedule, or cancel\n"
            "upcoming appointments directly in the app. You'll also receive confirmations\n"
            "and reminders.\n"
            "\n"
            "=== Is my information private? ===\n"
            "Yes. Your customer information is completely private and never visible to\n"
            "other customers."
        ),
    ),
    
    Section(
        id="business_faq",
        title="5. Business FAQ",
        keywords=[
            "manage", "schedule", "availability", "calendar", "working hours",
            "business profile", "services", "pricing", "team", "payments",
            "reporting", "analytics", "social media", "instagram", "facebook",
            "booking link", "share",
        ],
        content=(
            "=== How do I manage my business profile? ===\n"
            "Use the Business App to create and edit your profile, add services with pricing,\n"
            "set your availability, and manage your team.\n"
            "\n"
            "=== Can I share my SkeduleIt booking link? ===\n"
            "Yes! You can share your SkeduleIt booking link on Instagram, Facebook, WhatsApp,\n"
            "and other platforms so customers can book services directly.\n"
            "\n"
            "=== Does SkeduleIt handle payments? ===\n"
            "Yes. SkeduleIt includes integrated payment processing tools.\n"
            "\n"
            "=== Can I see business performance and earnings? ===\n"
            "Yes. The Business App includes reporting and analytics tools to track your\n"
            "transactions, popular services, and earnings."
        ),
    ),
    
    Section(
        id="support_help",
        title="6. Help & Support",
        keywords=[
            "help", "support", "contact", "assistance", "learn more",
            "onboarding", "get help", "customer service",
        ],
        content=(
            "=== Where can I get help? ===\n"
            "Support is available through the in-app 'Help & Support' section in both the\n"
            "Customer and Business apps.\n"
            "\n"
            "Additional resources:\n"
            "• SkeduleIt website\n"
            "• Social media platforms\n"
            "• Onboarding assistance for businesses during early rollout\n"
            "\n"
            "=== Where can I learn more about SkeduleIt? ===\n"
            "Information is available in the app's Help & Support section, on the SkeduleIt\n"
            "website, and across social media platforms."
        ),
    ),
    
    Section(
        id="account_management",
        title="7. Account Management",
        keywords=[
            "cancel account", "close account", "delete account",
            "deactivate", "remove account", "account closure",
        ],
        content=(
            "=== Can I cancel my account? ===\n"
            "Yes. Both customers and businesses can request account closure at any time.\n"
            "A confirmation step is included for security.\n"
            "\n"
            "For businesses: Closing your account will remove your business from SkeduleIt\n"
            "and cancel all future appointments."
        ),
    ),
]


# Public API: Functions to access the Knowledge Base
def get_full_knowledge_base() -> str:
    """Return the entire KB as one string — injected into every Gemini prompt."""
    return "\n\n---\n\n".join(
        f"### {s.title}\n{s.content}" for s in SECTIONS
    )


@dataclass
class RelevantContext:
    matched:   list[str]   # titles of sections that matched
    full_text: str         # the concatenated text of those sections


def get_relevant_context(query: str) -> RelevantContext:
    """
    Lightweight keyword pre-filter.  Scores each section, returns the ones
    with ≥1 hit sorted by score.  Falls back to the full KB when nothing
    matches.
    """
    lower = query.lower()

    scored = [
        (section, sum(1 for kw in section.keywords if kw in lower))
        for section in SECTIONS
    ]

    matched = sorted(
        (sec for sec, hits in scored if hits > 0),
        key=lambda sec: sum(1 for kw in sec.keywords if kw in lower),
        reverse=True,
    )

    selected = matched if matched else SECTIONS

    return RelevantContext(
        matched=[s.title for s in selected],
        full_text="\n\n---\n\n".join(f"### {s.title}\n{s.content}" for s in selected),
    )
