# Academic Paper Search MCP Server

[![smithery badge](https://smithery.ai/badge/@afrise/academic-search-mcp-server)](https://smithery.ai/server/@afrise/academic-search-mcp-server)

A [Model Context Protocol (MCP)](https://www.anthropic.com/news/model-context-protocol) server that enables searching and retrieving academic paper information from multiple sources.

The server provides LLMs with:
- Real-time academic paper search functionality  
- Access to paper metadata and abstracts
- Ability to retrieve full-text content when available
- Structured data responses following the MCP specification

While primarily designed for integration with Anthropic's Claude Desktop client, the MCP specification allows for potential compatibility with other AI models and clients that support tool/function calling capabilities (e.g. OpenAI's API).

**Note**: This software is under active development. Features and functionality are subject to change.

<a href="https://glama.ai/mcp/servers/kzsu1zzz9j"><img width="380" height="200" src="https://glama.ai/mcp/servers/kzsu1zzz9j/badge" alt="Academic Paper Search Server MCP server" /></a>

## Features

This server exposes the following tools:
- `search_papers`: Search for academic papers across multiple sources
  - Parameters:
    - `query` (str): Search query text
    - `limit` (int, optional): Maximum number of results to return (default: 10)
  - Returns: Formatted string containing paper details
  
- `fetch_paper_details`: Retrieve detailed information for a specific paper
  - Parameters:
    - `paper_id` (str): Paper identifier (DOI or Semantic Scholar ID)
    - `source` (str, optional): Data source ("crossref" or "semantic_scholar", default: "crossref")
  - Returns: Formatted string with comprehensive paper metadata including:
    - Title, authors, year, DOI
    - Venue, open access status, PDF URL (Semantic Scholar only)
    - Abstract and TL;DR summary (when available)

- `search_by_topic`: Search for papers by topic with optional date range filter
  - Parameters:
    - `topic` (str): Search query text (limited to 300 characters)
    - `year_start` (int, optional): Start year for date range 
    - `year_end` (int, optional): End year for date range
    - `limit` (int, optional): Maximum number of results to return (default: 10)
  - Returns: Formatted string containing search results including:
    - Paper titles, authors, and years
    - Abstracts and TL;DR summaries when available
    - Venue and open access information

## Setup


### Installing via Smithery

To install Academic Paper Search Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@afrise/academic-search-mcp-server):

```bash
npx -y @smithery/cli install @afrise/academic-search-mcp-server --client claude
```

***note*** this method is largely untested, as their server seems to be having trouble. you can follow the standalone instructions until smithery gets fixed. 

### Installing via uv (manual install): 

1. Install dependencies:
```sh
uv add "mcp[cli]" httpx
```

2. Set up required API keys in your environment or `.env` file:
```sh
#  These are not actually implemented
SEMANTIC_SCHOLAR_API_KEY=your_key_here 
CROSSREF_API_KEY=your_key_here  # Optional but recommended
```

3. Run the server:
```sh
uv run server.py
```

## Usage with Claude Desktop

1. Add the server to your Claude Desktop configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "academic-search": {
      "command": "uv",
      "args": ["run ", "/path/to/server/server.py"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "your_key_here",
        "CROSSREF_API_KEY": "your_key_here"
      }
    }
  }
}
```

2. Restart Claude Desktop


## Development

This server is built using:
- Python MCP SDK
- FastMCP for simplified server implementation
- httpx for API requests

## API Sources

- Semantic Scholar API
- Crossref API

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This license ensures that:

- You can freely use, modify, and distribute this software
- Any modifications must be open-sourced under the same license
- Anyone providing network services using this software must make the source code available
- Commercial use is allowed, but the software and any derivatives must remain free and open source

See the [LICENSE](LICENSE) file for the full license text.

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please note:
- Follow the existing code style and conventions
- Add tests for any new functionality
- Update documentation as needed
- Ensure your changes respect the AGPL-3.0 license terms

By contributing to this project, you agree that your contributions will be licensed under the AGPL-3.0 license.
