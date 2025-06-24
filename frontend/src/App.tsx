import './styles/index.css';


type AppProps = {
  // define props if any
};

const App: React.FC<AppProps> = (props) => {
  return <div className="flex items-center justify-center h-screen bg-gray-900">
      <h1 className="text-4xl font-bold text-blue-400">
        🚀 Tailwind is working!
      </h1>
    </div>;

};

export default App;
