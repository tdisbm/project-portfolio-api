import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from apps.project.models import Project

SEED_USERNAME = "TESTUSER"
SEED_PASSWORD = "TESTUSER"

_ADJECTIVES = [
    "Modern",
    "Scalable",
    "Lightweight",
    "Distributed",
    "Reactive",
    "Minimal",
    "Robust",
    "Automated",
    "Cloud-native",
    "Serverless",
    "Real-time",
    "Open-source",
    "Modular",
    "High-performance",
    "Secure",
]
_NOUNS = [
    "API",
    "Dashboard",
    "Pipeline",
    "Platform",
    "Service",
    "Bot",
    "Tool",
    "CLI",
    "Gateway",
    "Monitor",
    "Engine",
    "Hub",
    "Layer",
    "Framework",
    "System",
]
_DOMAINS = [
    "E-commerce",
    "Analytics",
    "CMS",
    "Portfolio",
    "Auth",
    "Billing",
    "Notification",
    "Search",
    "ML",
    "DevOps",
    "Logistics",
    "Finance",
    "Healthcare",
    "Education",
    "IoT",
]
_DESCRIPTION_TEMPLATES = [
    "A production-ready {noun} for handling {domain} workflows.",
    "Lightweight {noun} built for {domain} use cases with minimal overhead.",
    "Scalable {noun} with deep {domain} integrations and observability.",
    "Cloud-native {noun} designed for modern {domain} teams.",
    "An opinionated {noun} that simplifies {domain} operations end-to-end.",
]
_TECH_POOL = [
    "Python",
    "Django",
    "FastAPI",
    "Flask",
    "PostgreSQL",
    "Redis",
    "Celery",
    "TypeScript",
    "Angular",
    "React",
    "Vue",
    "Node.js",
    "GraphQL",
    "Docker",
    "Kubernetes",
    "Terraform",
    "GitHub Actions",
    "Go",
    "Rust",
    "Java",
    "Spring Boot",
    "Next.js",
    "Nginx",
    "Kafka",
]


class Command(BaseCommand):
    help = "Seed the database with N random projects linked to TESTUSER"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            "-n",
            dest="count",
            type=int,
            default=10,
            help="Number of projects to create (default: 10)",
        )

    def handle(self, *args, **options):
        count = options["count"]

        user, created = User.objects.get_or_create(username=SEED_USERNAME)
        if created:
            user.set_password(SEED_PASSWORD)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user '{SEED_USERNAME}'"))
        else:
            self.stdout.write(f"User '{SEED_USERNAME}' already exists, skipping creation")

        today = date.today()
        for _ in range(count):
            adj = random.choice(_ADJECTIVES)
            noun = random.choice(_NOUNS)
            domain = random.choice(_DOMAINS)
            name = f"{adj} {domain} {noun}"
            description = random.choice(_DESCRIPTION_TEMPLATES).format(
                noun=noun.lower(), domain=domain.lower()
            )
            technologies = random.sample(_TECH_POOL, k=random.randint(2, 6))

            days_ago = random.randint(0, 365 * 4)
            date_start = today - timedelta(days=days_ago)
            date_end_candidate = date_start + timedelta(days=random.randint(30, 540))
            date_end = date_end_candidate if date_end_candidate <= today else None

            Project.objects.create(
                user=user,
                name=name,
                description=description,
                technologies_used=technologies,
                date_start=date_start,
                date_end=date_end,
            )

        self.stdout.write(self.style.SUCCESS(f"Created {count} projects for '{SEED_USERNAME}'"))
