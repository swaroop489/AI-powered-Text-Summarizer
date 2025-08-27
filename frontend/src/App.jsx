import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
// import SingleFileSummarizer from "./SingleFileSummarizer";
// import MultiFileSummarizer from "./MultiFileSummarizer";

function App() {
  return (
    <Router>
      <Navbar />
      <div className="p-6">
        <Routes>

        </Routes>
      </div>
    </Router>
  );
}

export default App;
