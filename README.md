# D&D 5e Dynamic Character Sheet

# Multi-Platform
- Windows, Linux, MacOS, Android, iOS
- [Flet GUI](https://flet.dev/docs/)
- Python Backend
- SQLite Database

# File Structure:
- Project folder on Windows file system
- Use Windows for testing & file storage
- Use WSL (Linux) for git commands

# Initial Dev Environment Setup:
## Create Windows Virtual Environment:
    python -m venv .venv_win
## Install dependencies
    pip install -r requirements.txt
## Change python Interpreter
    Ctrl + Shift + P → select virtual environment interpreter
    Ctrl + Shift + P → Reload Window if necessary
## If using WSL
### Create Linux Virtual Environment:
    python3 -m venv .venv
## To run the UI (Powershell)
flet run .\main_fley.py

# Dev Environment Routine:
## Bash Activate Linux Virutal Environment:
    source .venv/bin/activate
## Powershell Activate Windows Virutal Environment
    .\.venv_win\Scripts\activate
## When installing a new library
    pip freeze > requirements.txt
## Seed Database
    python -m scripts.seed_db

# Resources
- https://github.com/BTMorton/dnd-5e-srd
- https://github.com/5e-bits/5e-database
- https://www.dnd5eapi.co/ 

# TODO 
- Add a License

## Feature List
- Scrolling Text Area that records the last actions (took 5 damage, used spell, etc.)
- Health and Mana (Spell Slot) Bars connected to HP-Text
- Dice Roller with breakdown of what dice were rolled and why (not abstracted away)

## Architecture
sequenceDiagram
    actor User
    participant View as AbilityScoreContainer (UI)
    participant PubSub as Flet Page PubSub
    participant Controller as CharacterSheetController
    participant Model as CharacterModel

    User->>View: Types "18" in Strength field
    View->>PubSub: send_all_on_topic(UI_ACTION, update_ability)
    PubSub->>Controller: handle_subscribe_topic_ui_action()
    Controller->>Model: ability_scores_list["strength"].base_score = 18
    Note over Model: Model state is now updated
    Controller->>PubSub: send_all_on_topic(MODEL_UPDATED)
    PubSub->>View: update_card_data()
    View->>Model: get_final_ability_score()
    Model-->>View: returns 18
    View->>User: UI Refreshes visually