import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="bg-white px-6 py-4 flex justify-between items-center shadow-lg">
      {/* Left: App Name */}
      <div className="text-2xl font-serif">
        <Link to="/">AI Text Summarizer</Link>
      </div>

      {/* Right: Navigation Links */}
      <div className="space-x-4">
        <Link
          to="/single"
          className="px-4 py-2 rounded hover:bg-gray-200"
        >
          Single File
        </Link>
        <Link
          to="/multi"
          className="px-4 py-2 rounded hover:bg-gray-200"
        >
          Multi File
        </Link>
      </div>
    </nav>
  );
}

export default Navbar;
