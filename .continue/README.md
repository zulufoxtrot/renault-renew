# Continue AI Configuration

This folder contains configuration and context for AI-assisted development.

## 📚 How to Use These Files

### 1. **Reference Context Files with @**

In Continue chat, use `@` to reference these files:

```
@PROJECT_CONTEXT.md - What is the architecture of this project?
@TASK_TEMPLATES.md - How do I add a new scraped field?
```

### 2. **Use in Prompts**

When asking Continue to make changes:

```
"Following @TASK_TEMPLATES.md, add a new field called 'warranty_months' to track warranty information"

"Using the patterns in @PROJECT_CONTEXT.md, create a new API endpoint for filtering by price range"

"Debug the scraper following @TASK_TEMPLATES.md debugging checklist"
```

### 3. **Custom Commands** (Optional)

If your Continue version supports custom commands in `config.json`:

- `/add-field` - Walk through adding a new scraped field
- `/debug-scraper` - Debug scraper issues
- `/review-scraper` - Review scraper code quality

### 4. **Rules (Auto-Applied)**

The rules in `.continuerules` are automatically applied when editing files that match their patterns.

## 📁 Files in This Folder

| File                 | Purpose                                   | How to Use                                                                   |
|----------------------|-------------------------------------------|------------------------------------------------------------------------------|
| `PROJECT_CONTEXT.md` | Architecture, file structure, conventions | Reference with `@PROJECT_CONTEXT.md` when asking about how the project works |
| `TASK_TEMPLATES.md`  | Step-by-step guides for common tasks      | Reference with `@TASK_TEMPLATES.md` when making specific changes             |
| `.continuerules`     | Auto-applied coding standards             | Automatically used - no action needed                                        |
| `config.json`        | Continue configuration                    | Automatically loaded by Continue                                             |
| `README.md`          | This file                                 | Usage instructions                                                           |

## 🎯 Common Workflows

### Adding a New Feature

```
Me: "I want to add support for scraping the vehicle's VIN number"

Continue: Following @TASK_TEMPLATES.md...
[AI walks through the steps]
```

### Debugging Issues

```
Me: "The scraper is failing to find vehicle titles. Check @PROJECT_CONTEXT.md for the scraper architecture and help me debug using @TASK_TEMPLATES.md"
```

### Understanding Code

```
Me: "Explain how the price tracking works. Reference @PROJECT_CONTEXT.md for the database schema"
```

### Code Review

```
Me: "Review my changes to app.py against the conventions in @PROJECT_CONTEXT.md"
```

## 🔧 Configuration

### Enabling Context Files

Continue automatically indexes markdown files in `.continue/`. No special configuration needed!

Just use `@filename` in your prompts.

### Custom Commands (Optional)

If using Continue v0.9.0+, the `config.json` includes custom commands. Access them via:

- Command palette (Cmd/Ctrl + Shift + P) → "Continue: ..."
- Or type `/command-name` in Continue chat

### Rules (Automatic)

The `.continuerules` file contains rules that are automatically applied when editing matching files:

- Python files → Type hints, error handling, PEP 8
- Flask routes → JSON responses, error handling
- Database code → Connection management, migrations

## 💡 Tips for AI Agents

1. **Always reference context first**: Start with `@PROJECT_CONTEXT.md` to understand the project
2. **Follow task templates**: Use `@TASK_TEMPLATES.md` for step-by-step guidance
3. **Respect conventions**: Rules in `.continuerules` are auto-applied
4. **Test changes**: Always suggest testing commands after making changes
5. **Explain reasoning**: Reference which file/section guided your decision

## 🚀 Quick Start

1. Open Continue chat (usually Cmd/Ctrl + L)
2. Type `@` to see available context files
3. Select a file or type the name
4. Ask your question with the context included

Example:

```
@PROJECT_CONTEXT.md What files do I need to modify to add a new database column?
```

## 📖 Learn More

- [Continue Documentation](https://continue.dev/docs)
- [Context Providers](https://continue.dev/docs/customize/context-providers)
- [Custom Commands](https://continue.dev/docs/customize/slash-commands)
