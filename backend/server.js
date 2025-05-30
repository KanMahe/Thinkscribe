const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB Connection (change if using Atlas)
mongoose.connect("mongodb://localhost:27017/referenceDB", {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Schema and Model
const paperSchema = new mongoose.Schema({
  title: String,
  authors: [String],
  year: Number,
  abstract: String,
  url: String,
});

const Paper = mongoose.model("Paper", paperSchema);

// POST /add-papers — Save selected papers
app.post("/add-papers", async (req, res) => {
  try {
    const papers = req.body;
    for (const paper of papers) {
      const exists = await Paper.findOne({ title: paper.title });
      if (!exists) {
        await Paper.create(paper);
      }
    }
    res.status(200).send("Papers saved successfully");
  } catch (error) {
    console.error("Error saving papers:", error);
    res.status(500).send("Server error while saving papers.");
  }
});

// GET /get-papers — Load saved papers for Reference Manager
app.get("/get-papers", async (req, res) => {
  try {
    const papers = await Paper.find().sort({ year: -1 }); // optional sort by year
    res.json(papers);
  } catch (error) {
    console.error("Error retrieving papers:", error);
    res.status(500).send("Server error while fetching papers.");
  }
});

// Start Server
app.listen(PORT, () => {
  console.log(`✅ Backend running at http://localhost:${PORT}`);
});
