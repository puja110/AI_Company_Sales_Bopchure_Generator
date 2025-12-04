#!/usr/bin/env python3
"""
Company Brochure Generator
Generate professional brochures from company websites using AI
"""

import argparse
from brochure_generator import BrochureGenerator


def main():
    parser = argparse.ArgumentParser(
        description='Generate a professional brochure from a company website'
    )
    parser.add_argument(
        'company_name',
        help='Name of the company'
    )
    parser.add_argument(
        'url',
        help='Company website URL (e.g., https://example.com)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output filename (default: {company_name}_brochure.md)',
        default=None
    )
    parser.add_argument(
        '--stream',
        '-s',
        action='store_true',
        help='Stream output with typewriter effect'
    )
    parser.add_argument(
        '--model',
        '-m',
        default='gpt-4o-mini',
        help='OpenAI model to use (default: gpt-4o-mini)'
    )
    
    args = parser.parse_args()
    
    if args.output is None:
        safe_name = args.company_name.replace(' ', '_').replace('/', '_')
        args.output = f"{safe_name}_brochure.md"
    
    try:
        generator = BrochureGenerator(model=args.model)
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease ensure you have a .env file with your OPENAI_API_KEY")
        return 1
    
    if args.stream:
        brochure_content = ""
        for chunk in generator.stream_brochure(args.company_name, args.url):
            brochure_content += chunk
    else:
        brochure_content = generator.create_brochure(args.company_name, args.url)
    
    if brochure_content:
        generator.save_brochure(brochure_content, args.output)
        return 0
    else:
        print("❌ Failed to generate brochure")
        return 1


if __name__ == "__main__":
    exit(main())