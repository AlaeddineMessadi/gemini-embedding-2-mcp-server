# Use Cases

The strongest fit for `gemini-embedding-2-mcp-server` is not generic "local RAG." It is multimodal local memory for agents that need to search mixed personal or team workspaces.

## 1. Cross-Modal Research Workspace

Index:
- markdown notes
- PDFs
- screenshots
- exported charts
- meeting clips

Then ask:
- `Find the PDF page that defines the pricing tiers.`
- `Search my screenshots for the dashboard version with the red warning banner.`
- `Find the note or slide where we compared the onboarding funnel to activation.`

## 2. Design and Product Libraries

Index:
- product requirement docs
- Figma export screenshots
- design system PDFs
- demo videos

Then ask:
- `Find examples of side navigation layouts with compact icon-only collapsed mode.`
- `Search only the design system docs folder for tokens related to spacing and elevation.`
- `Show me the exact PDF page where the component state table appears.`

## 3. Engineering Knowledge Search

Index:
- code-adjacent markdown
- architecture PDFs
- CSV exports
- incident notes

Then ask:
- `Search my work docs for incident response runbooks.`
- `Find the architecture page that mentions background workers and retries.`
- `Give me the surrounding context for the result about auth tokens so I can quote it accurately.`

## 4. Media-Heavy Personal Archives

Index:
- photo folders
- recorded calls
- voice notes
- short clips

Then ask:
- `Find clips related to launch planning.`
- `Search my image folder for whiteboard photos about metrics.`
- `Find audio or video files discussing vendor pricing.`

## Why These Workflows Matter

Gemini Embedding 2 matters when your useful information is not all plain text. This server is designed for the common real-world case where the "memory" an agent needs is spread across:
- documents
- visual pages
- images
- audio
- video

and must still resolve back to exact local files and locations.
