# Muse Connector — How to connect UKGraph to Muse

## Muse compatibility

Our MCP servers follow the Model Context Protocol (MCP) standard.
Muse works with MCP servers in three ways:

### 1. Custom Connector (recommended)

Muse can create a Custom Connector for any API. Ask Muse:

> "Connect to https://mcp.ukgraph.dev/mcp"

Muse will:
1. Discover our tools
2. Store credentials in Secure Credentials Store
3. Make tools available in conversations

### 2. MCP Server URL

If we deploy a remote MCP server, Muse can connect directly:

```
https://mcp.ukgraph.dev/mcp
```

### 3. Muse Code (for developers)

Muse Code supports MCP servers. Add to config:

```json
{
  "mcpServers": {
    "ukgraph": {
      "command": "python",
      "args": ["-m", "mcp.uk_boring_mcp", "--serve"]
    }
  }
}
```

## Tool names Muse will see

```
resolve_place          - Turn postcode into Place with all jurisdictions
get_area_services      - What services are available in this area
get_area_workflows     - What workflows can I do here
move_home              - Start the move-home workflow
check_mot              - Check MOT history
check_vehicle_tax      - Check vehicle tax
check_council_tax      - Check council tax band
check_company          - Look up a company
preflight              - What info do I need
verify_receipt         - Verify a confirmation
list_national_workflows - All UK-wide workflows
earn                   - Find economic opportunities
list_painful_tasks     - Most annoying UK tasks
get_painful_task       - Detailed workflow for a task
achieve_goal           - Start working toward a goal
list_goals             - Available goals
get_opportunities      - Opportunities in an area
```

## What Muse can do with these tools

```
User: "I'm moving to Oldham"

Muse calls: resolve_place(postcode="OL1 1AA")
→ Place: Oldham, Council: Oldham MBC

Muse calls: move_home(new_postcode="OL1 1AA")
→ 7 steps identified, receipt patterns ready

Muse: "I can handle 5 of these steps for you.
       I need your council tax reference.
       2 steps require you to do them directly."
```

## What Muse CAN'T do (yet)

| Limitation | Why | Workaround |
|------------|-----|------------|
| Can't submit GOV.UK forms | Auth required | USER_HANDOFF step |
| Can't access DVLA directly | Auth required | User takes over |
| Can't pay for services | Money transfer | APPROVAL step |
| Can't sign legally | Attestation required | DECLARATION step |

## Key design principle

Every workflow step has an `action_class`:

```
AUTO              - Muse executes fully
APPROVAL          - Muse prepares, user approves
AUTH_HANDOFF      - User takes over for login
DECLARATION       - User must personally attest
USER_HANDOFF      - Cannot be agent-completed
```

Muse never improvises what "success" means.
UKGraph tells Muse what success means before it starts.
