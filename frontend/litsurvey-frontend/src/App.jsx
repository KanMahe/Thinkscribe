import { useState, useEffect } from "react";
import {
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Container,
  Paper,
  CircularProgress,
  Checkbox,
} from "@mui/material";
import { saveAs } from "file-saver";

function App() {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(10);
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Fetching papers...");
  const [selectedPapers, setSelectedPapers] = useState(new Set());
  const [savedPapers, setSavedPapers] = useState([]);
  const [bibtexPreview, setBibtexPreview] = useState("");
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    if (loading) {
      const messages = [
        "Fetching papers...",
        "Analyzing abstracts...",
        "Summarizing key ideas...",
        "Generating concise summary table...",
      ];
      let index = 0;
      setLoadingMessage(messages[index]);
      const interval = setInterval(() => {
        index = (index + 1) % messages.length;
        setLoadingMessage(messages[index]);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const fetchPapers = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:5000/fetch_and_store?query=${encodeURIComponent(query)}&limit=${limit}`
      );
      const data = await response.json();
      if (response.ok) {
        if (data.processed && data.processed.length > 0) {
          setPapers(data.processed);
        } else {
          alert("No papers found or processed data is empty.");
        }
      } else {
        alert(data.message || "An error occurred while fetching papers.");
      }
    } catch (error) {
      alert("An error occurred while fetching papers.");
    } finally {
      setLoading(false);
    }
  };

  const deletePaper = (index) => {
    const newPapers = [...papers];
    newPapers.splice(index, 1);
    setPapers(newPapers);
  };

  const generateBibtex = async () => {
    const entries = await Promise.all(
      papers.map((paper) =>
        fetch("http://localhost:5000/bibtex", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(paper),
        }).then((res) => res.json())
      )
    );
    const bibtexText = entries.map((e) => e.bibtex).join("\n\n");
    setBibtexPreview(bibtexText);
    setShowPreview(true);
  };

  const addSelectedPapers = async () => {
    if (selectedPapers.size === 0) {
      alert("No papers selected!");
      return;
    }
    const papersToAdd = papers.filter((_, i) => selectedPapers.has(i));
    try {
      const response = await fetch("http://localhost:5000/add-papers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(papersToAdd),
      });
      if (response.ok) {
        alert("Papers saved successfully!");
        setSelectedPapers(new Set());
        fetchSavedPapers();
      } else {
        alert("Failed to save papers");
      }
    } catch (error) {
      alert("Error saving papers");
    }
  };

  const fetchSavedPapers = async () => {
    try {
      const res = await fetch("http://localhost:5000/get-papers");
      const data = await res.json();
      setSavedPapers(data);
    } catch (err) {
      console.error("Error fetching saved papers:", err);
    }
  };

  useEffect(() => {
    fetchSavedPapers();
  }, []);

  return (
    <Container maxWidth="lg" sx={{ paddingTop: 4 }}>
      <div style={{ display: "flex", gap: "16px" }}>
        <Paper elevation={3} sx={{ width: 280, padding: 2, maxHeight: "80vh", overflowY: "auto", bgcolor: "#f9f9f9", flexShrink: 0 }}>
          <h2>Reference Manager</h2>
          {savedPapers.length === 0 ? (
            <p>No saved papers</p>
          ) : (
            savedPapers.map((paper, i) => (
              <div key={i} style={{ marginBottom: 12 }}>
                <a href={paper.url} target="_blank" rel="noopener noreferrer" style={{ fontWeight: 'bold' }}>{paper.title}</a>
                <br />
                <small>{paper.authors?.join(", ")}</small>
              </div>
            ))
          )}
        </Paper>

        <Paper sx={{ flexGrow: 1, padding: 2 }}>
          <h1 className="text-2xl font-bold mb-4">Literature Survey Helper</h1>

          <div className="flex gap-4 mb-6">
            <TextField fullWidth label="Search Research Problem" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === "Enter" && fetchPapers()} />
            <TextField label="Limit" type="number" value={limit} onChange={(e) => setLimit(Math.max(1, Number(e.target.value)))} inputProps={{ min: 1 }} sx={{ width: 100 }} />
            <Button variant="contained" onClick={fetchPapers}>Search</Button>
          </div>

          <div className="flex gap-4 mb-6 items-center">
            <input type="file" accept="application/pdf" onChange={async (e) => {
              const file = e.target.files[0];
              if (!file) return;
              const formData = new FormData();
              formData.append("pdf", file);
              setLoading(true);
              try {
                const res = await fetch("http://localhost:5000/upload_pdf", {
                  method: "POST",
                  body: formData,
                });
                const data = await res.json();
                if (res.ok && data.processed) {
                  setPapers(data.processed);
                  alert("PDF uploaded and summarized!");
                } else {
                  alert(data.message || "Processing failed.");
                }
              } catch (err) {
                alert("Error uploading PDF.");
              } finally {
                setLoading(false);
              }
            }} />
            <span style={{ fontSize: "0.9rem", color: "#555" }}>Upload a research PDF to summarize</span>
          </div>

          {loading && (
            <div className="flex flex-col items-center gap-4 mt-4">
              <CircularProgress />
              <p className="text-gray-600 text-sm">{loadingMessage}</p>
            </div>
          )}

          {!loading && papers.length > 0 && (
            <>
              <Paper>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Title</TableCell>
                      <TableCell>Authors</TableCell>
                      <TableCell>Abstract</TableCell>
                      <TableCell>Techniques</TableCell>
                      <TableCell>Year</TableCell>
                      <TableCell>URL</TableCell>
                      <TableCell>Action</TableCell>
                      <TableCell padding="checkbox">
                        <Checkbox
                          indeterminate={selectedPapers.size > 0 && selectedPapers.size < papers.length}
                          checked={papers.length > 0 && selectedPapers.size === papers.length}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedPapers(new Set(papers.map((_, i) => i)));
                            } else {
                              setSelectedPapers(new Set());
                            }
                          }}
                        />
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {papers.map((paper, index) => (
                      <TableRow key={index}>
                        <TableCell>{paper.title}</TableCell>
                        <TableCell>{paper.authors?.join(", ")}</TableCell>
                        <TableCell>{paper.abstract || "N/A"}</TableCell>
                        <TableCell>{paper.techniques?.join(", ") || "N/A"}</TableCell>
                        <TableCell>{paper.year}</TableCell>
                        <TableCell>{paper.url ? (<a href={paper.url} target="_blank" rel="noopener noreferrer">View Paper</a>) : ("N/A")}</TableCell>
                        <TableCell><Button color="error" onClick={() => deletePaper(index)}>Delete</Button></TableCell>
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedPapers.has(index)}
                            onChange={() => {
                              const newSelected = new Set(selectedPapers);
                              if (newSelected.has(index)) newSelected.delete(index);
                              else newSelected.add(index);
                              setSelectedPapers(newSelected);
                            }}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Paper>

              <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
                <Button variant="contained" color="primary" onClick={addSelectedPapers} disabled={selectedPapers.size === 0}>Add Selected</Button>
                <Button variant="contained" color="success" onClick={generateBibtex} disabled={papers.length === 0}>Download BibTeX</Button>
              </div>
            </>
          )}
        </Paper>

        {showPreview && (
          <div style={{ position: "fixed", top: 0, left: 0, width: "100vw", height: "100vh", backgroundColor: "rgba(0, 0, 0, 0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
            <div style={{ backgroundColor: "white", padding: 20, borderRadius: 8, maxHeight: "90vh", overflowY: "auto", width: "80%" }}>
              <h2>BibTeX Preview</h2>
              <pre style={{ backgroundColor: "#f0f0f0", padding: 12, borderRadius: 4, whiteSpace: "pre-wrap", wordWrap: "break-word" }}>{bibtexPreview}</pre>
              <div style={{ marginTop: 12, textAlign: "right" }}>
                <Button variant="outlined" onClick={() => {
                  const blob = new Blob([bibtexPreview], { type: "text/plain;charset=utf-8" });
                  saveAs(blob, "references.bib");
                }} style={{ marginRight: 10 }}>Download .bib</Button>
                <Button variant="contained" onClick={() => setShowPreview(false)}>Close</Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Container>
  );
}

export default App;
