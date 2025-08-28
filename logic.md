``` mermaid

graph TD

    55["User<br>External Actor"]
    subgraph 44["Asset Management System<br>Various"]
        72["Fonts<br>TTF/OTF"]
        subgraph 45["Game Specific Assets<br>PNG/MP4"]
            76["Game Backgrounds<br>PNG/MP4"]
            77["Boss Characters<br>PNG"]
            78["Game Buttons<br>PNG"]
            79["Game Maps<br>PNG"]
            80["NPCs<br>PNG"]
        end
        subgraph 46["General Screen Elements<br>PNG"]
            73["Icons<br>PNG"]
            74["Character Sprites<br>PNG"]
            75["Misc. Screen Elements<br>PNG"]
        end
    end
    subgraph 47["Database Management System<br>SQLite"]
        70["Database Initialization<br>Python/SQLite"]
        71["Database Files<br>SQLite"]
        %% Edges at this level (grouped by source)
        47["Database Management System<br>SQLite"] -->|Accesses| 71["Database Files<br>SQLite"]
        70["Database Initialization<br>Python/SQLite"] -->|Creates/Sets up| 71["Database Files<br>SQLite"]
    end
    subgraph 48["Backend Services<br>Python"]
        69["Data Validation<br>Python"]
        subgraph 49["Class Management<br>Python"]
            66["Class Model<br>Python"]
            67["Class Registration Service<br>Python"]
            68["Class Loading Service<br>Python"]
        end
        subgraph 50["Authentication and User Management<br>Python"]
            64["Login Service<br>Python"]
            65["Registration Service<br>Python"]
        end
    end
    subgraph 51["Frontend System<br>Python/PyQt"]
        63["UI Design Assets<br>Qt Designer UI"]
        subgraph 52["UI Screens<br>Python/PyQt"]
            58["Login Screen<br>Python/PyQt"]
            59["Class Registration Screen<br>Python/PyQt"]
            60["List Classes Screen<br>Python/PyQt"]
            subgraph 53["Game Screen<br>Python/PyQt"]
                61["Game Screen UI<br>Python/PyQt"]
                62["Game Logic &amp; Flow<br>Python"]
            end
        end
        %% Edges at this level (grouped by source)
        52["UI Screens<br>Python/PyQt"] -->|Uses UI definitions| 63["UI Design Assets<br>Qt Designer UI"]
    end
    subgraph 54["Core Application Orchestration<br>Python"]
        56["Main Application Entry Point<br>Python"]
        57["Configuration Management<br>JSON"]
        %% Edges at this level (grouped by source)
        56["Main Application Entry Point<br>Python"] -->|Reads configuration| 57["Configuration Management<br>JSON"]
    end
    %% Edges at this level (grouped by source)
    51["Frontend System<br>Python/PyQt"] -->|Loads UI assets| 44["Asset Management System<br>Various"]
    51["Frontend System<br>Python/PyQt"] -->|Requests data/services| 48["Backend Services<br>Python"]
    53["Game Screen<br>Python/PyQt"] -->|Loads game assets| 45["Game Specific Assets<br>PNG/MP4"]
    52["UI Screens<br>Python/PyQt"] -->|Loads general UI assets| 46["General Screen Elements<br>PNG"]
    48["Backend Services<br>Python"] -->|Performs CRUD operations| 47["Database Management System<br>SQLite"]
    56["Main Application Entry Point<br>Python"] -->|Initializes UI| 51["Frontend System<br>Python/PyQt"]
    55["User<br>External Actor"] -->|Interacts with| 56["Main Application Entry Point<br>Python"]
```