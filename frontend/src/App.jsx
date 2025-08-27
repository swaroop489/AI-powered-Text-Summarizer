import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import SingleFileSummarizer from "./components/SingleFileSummarizer";
import MultiFileSummarizer from "./components/MultiFileSummarizer";

function App() {
  return (
    <div className="bg-gray-100">
    <Router>
      <Navbar />
      <div className="p-6">
        <Routes>
          <Route path="/" element={<SingleFileSummarizer />} />
          <Route path="/single" element={<SingleFileSummarizer />} />
          <Route path="/multi" element={<MultiFileSummarizer/>} />
        </Routes>
      </div>
    </Router>
    </div>
  );
}

export default App;
