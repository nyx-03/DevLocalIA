const state = {
        mode: "chat",
      };

      const outputEl = document.getElementById("output");
      const statusEl = document.getElementById("status");
      const healthEl = document.getElementById("health");
      const modeEl = document.getElementById("mode");
      const projectNameEl = document.getElementById("projectName");
      const fileCountEl = document.getElementById("fileCount");
      const chunkCountEl = document.getElementById("chunkCount");
      const activityEl = document.getElementById("activity");

      document.querySelectorAll(".mode-tabs button").forEach((tab) => {
        tab.addEventListener("click", () => {
          document.querySelectorAll(".mode-tabs button").forEach((t) => t.classList.remove("active"));
          tab.classList.add("active");
          state.mode = tab.dataset.mode;
          modeEl.textContent = state.mode;
        });
      });

      document.querySelectorAll(".chip").forEach((chip) => {
        chip.addEventListener("click", () => {
          const suggestion = chip.dataset.suggest;
          if (suggestion) {
            document.getElementById("query").value = suggestion;
          }
        });
      });

      function escapeHtml(value) {
        return value
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/\"/g, "&quot;")
          .replace(/'/g, "&#039;");
      }

      function renderMarkdown(markdown) {
        if (!markdown) return "";

        const codeBlocks = [];
        let text = markdown.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
          const index = codeBlocks.length;
          codeBlocks.push({ lang: lang || "", code });
          return `@@CODE${index}@@`;
        });

        text = escapeHtml(text);

        const lines = text.split(/\r?\n/);
        let html = "";
        let inUl = false;
        let inOl = false;

        const closeLists = () => {
          if (inUl) {
            html += "</ul>";
            inUl = false;
          }
          if (inOl) {
            html += "</ol>";
            inOl = false;
          }
        };

        const formatInline = (line) => {
          let out = line;
          out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
          out = out.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
          out = out.replace(/\*(.+?)\*/g, "<em>$1</em>");
          out = out.replace(/\[(.+?)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
          return out;
        };

        for (const line of lines) {
          if (/^######\s+/.test(line)) {
            closeLists();
            html += `<h6>${formatInline(line.replace(/^######\s+/, ""))}</h6>`;
            continue;
          }
          if (/^#####\s+/.test(line)) {
            closeLists();
            html += `<h5>${formatInline(line.replace(/^#####\s+/, ""))}</h5>`;
            continue;
          }
          if (/^####\s+/.test(line)) {
            closeLists();
            html += `<h4>${formatInline(line.replace(/^####\s+/, ""))}</h4>`;
            continue;
          }
          if (/^###\s+/.test(line)) {
            closeLists();
            html += `<h3>${formatInline(line.replace(/^###\s+/, ""))}</h3>`;
            continue;
          }
          if (/^##\s+/.test(line)) {
            closeLists();
            html += `<h2>${formatInline(line.replace(/^##\s+/, ""))}</h2>`;
            continue;
          }
          if (/^#\s+/.test(line)) {
            closeLists();
            html += `<h1>${formatInline(line.replace(/^#\s+/, ""))}</h1>`;
            continue;
          }
          if (/^>\s+/.test(line)) {
            closeLists();
            html += `<blockquote>${formatInline(line.replace(/^>\s+/, ""))}</blockquote>`;
            continue;
          }
          if (/^---\s*$/.test(line)) {
            closeLists();
            html += "<hr />";
            continue;
          }
          if (/^\s*\d+\.\s+/.test(line)) {
            if (!inOl) {
              closeLists();
              html += "<ol>";
              inOl = true;
            }
            html += `<li>${formatInline(line.replace(/^\s*\d+\.\s+/, ""))}</li>`;
            continue;
          }
          if (/^\s*[-*+]\s+/.test(line)) {
            if (!inUl) {
              closeLists();
              html += "<ul>";
              inUl = true;
            }
            html += `<li>${formatInline(line.replace(/^\s*[-*+]\s+/, ""))}</li>`;
            continue;
          }
          if (line.trim() === "") {
            closeLists();
            html += '<div class="md-gap"></div>';
            continue;
          }
          closeLists();
          html += `<p>${formatInline(line)}</p>`;
        }

        closeLists();

        html = html.replace(/@@CODE(\d+)@@/g, (match, index) => {
          const block = codeBlocks[Number(index)];
          if (!block) return "";
          const code = escapeHtml(block.code);
          const langAttr = block.lang ? ` data-lang="${block.lang}"` : "";
          return `<pre><code${langAttr}>${code}</code></pre>`;
        });

        return html;
      }

      async function callApi(path, payload) {
        const response = await fetch(path, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        if (!response.ok) {
          const text = await response.text();
          throw new Error(text || `HTTP ${response.status}`);
        }
        return response.json();
      }

      async function refreshStats() {
        const projectId = parseInt(document.getElementById("projectId").value, 10);
        if (!projectId || Number.isNaN(projectId)) return;
        try {
          const response = await fetch(`/projects/${projectId}/stats`);
          if (!response.ok) return;
          const data = await response.json();
          projectNameEl.textContent = data.project_name || "-";
          fileCountEl.textContent = data.file_count ?? "-";
          chunkCountEl.textContent = data.chunk_count ?? "-";
        } catch (err) {
          // noop
        }
      }

      document.getElementById("healthBtn").addEventListener("click", async () => {
        statusEl.textContent = "Vérification de l'API...";
        statusEl.classList.add("pulse");
        activityEl.textContent = "Ping de l'API.";
        try {
          const response = await fetch("/health");
          const data = await response.json();
          healthEl.textContent = data.status || "ok";
          statusEl.textContent = "API accessible.";
        } catch (err) {
          healthEl.textContent = "indisponible";
          statusEl.textContent = `Erreur API : ${err.message}`;
        } finally {
          statusEl.classList.remove("pulse");
        }
      });

      document.getElementById("indexBtn").addEventListener("click", async () => {
        const projectPath = document.getElementById("projectPath").value.trim();
        if (!projectPath) {
          outputEl.textContent = "Chemin du projet requis.";
          return;
        }

        statusEl.textContent = "Indexation en cours...";
        statusEl.classList.add("pulse");
        activityEl.textContent = "Indexation en cours.";
        outputEl.textContent = "";
        outputEl.classList.remove("markdown");

        try {
          const result = await callApi("/projects/index", { root_path: projectPath });
          document.getElementById("projectId").value = result.project_id;
          projectNameEl.textContent = result.project_name || "-";
          fileCountEl.textContent = result.file_count ?? "-";
          chunkCountEl.textContent = result.chunk_count ?? "-";
          outputEl.textContent =
            `Indexation terminée.\n` +
            `Projet: ${result.project_name}\n` +
            `Chemin: ${result.root_path}\n` +
            `Fichiers: ${result.file_count}\n` +
            `Chunks: ${result.chunk_count}\n` +
            `Ignorés: ${result.skipped_count}`;
          statusEl.textContent = "Indexation terminée.";
          activityEl.textContent = "Indexation terminée.";
        } catch (err) {
          outputEl.textContent = `Erreur : ${err.message}`;
          statusEl.textContent = "Échec.";
          activityEl.textContent = "Erreur d'indexation.";
        } finally {
          statusEl.classList.remove("pulse");
        }
      });

      document.getElementById("runBtn").addEventListener("click", async () => {
        const projectId = parseInt(document.getElementById("projectId").value, 10);
        const query = document.getElementById("query").value.trim();
        const focus = document.getElementById("focus").value.trim();
        const maxChunks = parseInt(document.getElementById("maxChunks").value, 10);
        const style = document.getElementById("style").value;

        if (!projectId || Number.isNaN(projectId)) {
          outputEl.textContent = "ID de projet requis.";
          return;
        }
        if (state.mode !== "docs" && !query) {
          outputEl.textContent = "Question ou cible requise pour ce mode.";
          return;
        }

        statusEl.textContent = `Exécution ${state.mode}...`;
        statusEl.classList.add("pulse");
        activityEl.textContent = `Exécution ${state.mode}.`;
        outputEl.textContent = "";
        outputEl.classList.remove("markdown");

        try {
          let result;
          if (state.mode === "chat") {
            result = await callApi("/chat", { project_id: projectId, query, max_chunks: maxChunks });
            outputEl.classList.add("markdown");
            outputEl.innerHTML = renderMarkdown(result.answer || "");
          } else if (state.mode === "docs") {
            result = await callApi("/docs/generate", { project_id: projectId, focus: focus || null, max_chunks: maxChunks });
            outputEl.classList.add("markdown");
            outputEl.innerHTML = renderMarkdown(result.markdown || "");
          } else if (state.mode === "tests") {
            result = await callApi("/tests/generate", { project_id: projectId, target: query, max_chunks: maxChunks, framework: "pytest" });
            outputEl.textContent = result.test_code || "";
          } else if (state.mode === "refactor") {
            result = await callApi("/refactor/suggest", { project_id: projectId, target: query, max_chunks: maxChunks, style });
            outputEl.textContent = result.refactor || "";
          }
          statusEl.textContent = "Terminé.";
          activityEl.textContent = "Terminé.";
        } catch (err) {
          outputEl.textContent = `Erreur : ${err.message}`;
          statusEl.textContent = "Échec.";
          activityEl.textContent = "Erreur lors de l'exécution.";
        } finally {
          statusEl.classList.remove("pulse");
        }
      });

      document.getElementById("clearBtn").addEventListener("click", () => {
        outputEl.textContent = "";
        outputEl.classList.remove("markdown");
        activityEl.textContent = "Sortie effacée.";
      });

      document.getElementById("statsBtn").addEventListener("click", async () => {
        activityEl.textContent = "Rechargement des stats.";
        await refreshStats();
        activityEl.textContent = "Stats mises à jour.";
      });
