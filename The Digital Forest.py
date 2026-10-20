<!DOCTYPE html>
<html>
<head>
    <title>The Digital Forest</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        #game-container {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
            margin-top: 20px;
        }

        #grid {
            display: grid;
            grid-template-columns: repeat(3, 60px);
            gap: 5px;
        }

        .tile {
            width: 60px;
            height: 60px;
            border: 1px solid #00ff00;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            transition: all 0.3s;
        }

        .stats {
            background: #000;
            padding: 20px;
            border: 1px solid #00ff00;
        }

        .progress-bar {
            height: 20px;
            background: #333;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: #00ff00;
            transition: width 0.3s;
        }

        .controls {
            margin: 20px 0;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }

        button {
            background: #000;
            color: #00ff00;
            border: 1px solid #00ff00;
            padding: 10px;
            cursor: pointer;
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        button:hover:enabled {
            background: #00ff0022;
        }

        #message-log {
            height: 150px;
            overflow-y: auto;
            border: 1px solid #00ff00;
            padding: 10px;
            margin-top: 20px;
            width: 100%;
            max-width: 700px;
            background: #111;
        }
    </style>
</head>
<body>
    <h1>🌲 The Digital Forest 🌲</h1>
    <div id="game-container">
        <div>
            <div id="grid"></div>
            <div class="controls">
                <button onclick="move('up')">↑ Up</button>
                <button onclick="move('left')">← Left</button>
                <button onclick="move('right')">→ Right</button>
                <button onclick="move('down')">↓ Down</button>
            </div>
        </div>
        <div class="stats">
            <h3>Round: <span id="round">1</span>/20</h3>
            <div>Health: <span id="health">100</span></div>
            <div class="progress-bar"><div id="health-bar" class="progress-fill" style="width: 100%"></div></div>
            <div>Energy: <span id="energy">100</span></div>
            <div class="progress-bar"><div id="energy-bar" class="progress-fill" style="width: 100%"></div></div>
            <h4>Legend</h4>
            <div>🌿: Grass</div>
            <div>💧: Water</div>
            <div>🌳: Tree</div>
            <div>☠️: Danger</div>
            <div>🚧: Obstacle</div>
            <div>🍎: Fruit</div>
        </div>
    </div>
    <div id="message-log"></div>

    <script>
        const TILE_EFFECTS = {
            "G": { health: 0, energy: 0, name: "Grass", icon: "🌿" },
            "W": { health: 0, energy: 10, name: "Water", icon: "💧" },
            "T": { health: 0, energy: 0, name: "Tree", icon: "🌳" },
            "DZ": { health: -20, energy: -10, name: "Danger Zone", icon: "☠️" },
            "O": { health: -5, energy: -5, name: "Obstacle", icon: "🚧" },
            "F": { health: 15, energy: 15, name: "Fruit", icon: "🍎" }
        };

        const messageLog = document.getElementById("message-log");
        let gameState = null;

        function renderGrid(visibleArea) {
            const gridDiv = document.getElementById("grid");
            gridDiv.innerHTML = "";

            for (const row of visibleArea || []) {
                for (const tileCode of row) {
                    const tileDiv = document.createElement("div");
                    tileDiv.className = "tile";

                    if (tileCode === "P") {
                        tileDiv.style.background = "#00ff00";
                        tileDiv.style.color = "#000";
                        tileDiv.textContent = "🧑";
                    } else if (tileCode === null) {
                        tileDiv.textContent = "";
                        tileDiv.style.background = "#222";
                    } else {
                        tileDiv.textContent = TILE_EFFECTS[tileCode].icon;
                    }

                    gridDiv.appendChild(tileDiv);
                }
            }
        }

        function renderState(state) {
            if (!state) return;
            gameState = state;

            document.getElementById("health").textContent = state.health;
            document.getElementById("energy").textContent = state.energy;
            document.getElementById("round").textContent = state.round;
            document.getElementById("health-bar").style.width = `${Math.max(0, state.health)}%`;
            document.getElementById("energy-bar").style.width = `${Math.max(0, state.energy)}%`;

            renderGrid(state.visible_area);
            messageLog.innerHTML = (state.message_log || []).map(msg => `<div>${msg}</div>`).join("");
        }

        async function sendRequest(url, options = {}) {
            const response = await fetch(url, {
                headers: { "Content-Type": "application/json" },
                ...options
            });

            if (!response.ok) {
                throw new Error(`Request failed: ${response.status}`);
            }

            return response.json();
        }

        async function move(direction) {
            if (gameState && gameState.game_over) return;

            try {
                const result = await sendRequest("/api/move", {
                    method: "POST",
                    body: JSON.stringify({ direction })
                });
                renderState(result.state);
            } catch (error) {
                console.error(error);
                messageLog.innerHTML = "<div>Unable to connect to the game server.</div>";
            }
        }

        async function initializeGame() {
            try {
                const state = await sendRequest("/api/state");
                renderState(state);
            } catch (error) {
                console.error(error);
                messageLog.innerHTML = "<div>Unable to connect to the game server. Start the backend with: python app.py</div>";
            }
        }

        document.addEventListener("keydown", function (event) {
            if (gameState && gameState.game_over) return;

            if (event.key === "ArrowUp") move("up");
            if (event.key === "ArrowDown") move("down");
            if (event.key === "ArrowLeft") move("left");
            if (event.key === "ArrowRight") move("right");
        });

        window.onload = initializeGame;
    </script>
</body>
</html>
