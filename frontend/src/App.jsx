import { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const searchMovies = async (e) => {
    e.preventDefault();
    const response = await fetch(`http://localhost:8000/search?q=${query}`);
    const data = await response.json();
    setResults(data);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Movie Search</h1>
        <form onSubmit={searchMovies}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a movie..."
          />
          <button type="submit">Search</button>
        </form>
      </header>
      <main>
        <div className="results">
          {results.map((movie, index) => (
            <div key={index} className="result">
              <h2>{movie.title}</h2>
              <p>{movie.overview}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default App;
