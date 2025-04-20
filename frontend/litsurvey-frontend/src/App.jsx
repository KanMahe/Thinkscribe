import { useState, useEffect } from "react";
import { Link } from 'react-router-dom';
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
} from "@mui/material";
import { saveAs } from "file-saver";

function App() {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(10);
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Fetching papers...");

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
      }, 1000); // update every 1 second
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
      
      // Log data to ensure it's being returned
      console.log('Fetched Data:', data);

      if (response.ok) {
        if (data.processed && data.processed.length > 0) {
          setPapers(data.processed); // Populate papers if processed data is available
        } else {
          console.error("No papers found or processed data is empty.");
          alert("No papers found or processed data is empty.");
        }
      } else {
        console.error("API Error:", data.message || "Unknown error");
        alert(data.message || "An error occurred while fetching papers.");
      }
    } catch (error) {
      console.error("Error fetching papers:", error);
      alert("An error occurred while fetching papers.");
    } finally {
      setLoading(false); // Ensure the loading state is reset
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
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(paper),
        }).then((res) => res.json())
      )
    );

    const bibtexText = entries.map((e) => e.bibtex).join("\n\n");

    const blob = new Blob([bibtexText], { type: "text/plain;charset=utf-8" });
    saveAs(blob, "references.bib");
  };

  return (
    <Container maxWidth="md" sx={{ paddingTop: 4 }}>
      <h1 className="text-2xl font-bold mb-4">Literature Survey Helper</h1>

      <div className="flex gap-4 mb-6">
        <TextField
          fullWidth
          label="Search Research Problem"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && fetchPapers()}
        />
        <TextField
          label="Limit"
          type="number"
          value={limit}
          onChange={(e) => setLimit(Math.max(1, Number(e.target.value)))}
     
          slotProps={{
            input:{
              min:1,
            },
          }}
          sx={{ width: 100 }}
        />
        <Button variant="contained" onClick={fetchPapers}>
          Search
        </Button>
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
                  <TableCell>Year</TableCell>
                  <TableCell>Abstract</TableCell>
                  <TableCell>Techniques</TableCell>
                  <TableCell>URL</TableCell>
                  <TableCell>Action</TableCell>
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
                    <TableCell>
                      {paper.url && typeof paper.url === 'string' && paper.url !== '' ? (
                          <Link href={paper.url} target="_blank" rel="noopener noreferrer">
                            View Paper
                          </Link>
                          ) : (
                          "N/A"
                      )}

                    </TableCell>
                    <TableCell>
                      <Button color="error" onClick={() => deletePaper(index)}>
                        Delete
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
          <div className="mt-6">
            <Button variant="contained" color="success" onClick={generateBibtex}>
              Download BibTeX
            </Button>
          </div>
        </>
      )}
    </Container>
  );
}

export default App;