import {Route, Routes} from 'react-router-dom';



import BalancePage from './pages/Balance';
import ChartPage from './pages/Chart';
import HomePage from './pages/Home';
import PopolPage from './pages/Popol';
import SearchPage from './pages/Search';
import LoginPage from './pages/Login';

import NavBar from './component/layout/NavBar.js';

function App() {
  

  return (
    <>
      <NavBar/>
      
      <Routes>
        <Route path='/' element={<LoginPage/>} />

        <Route path='/home' element={<HomePage/>} />
        
        <Route path='/home/chart' element={<ChartPage/>} />

        <Route path='/home/balance' element={<BalancePage/>} />

        <Route path='/home/popol' element={<PopolPage/>} />

        <Route path='/home/search' element={<SearchPage/>} />

      </Routes>
      

    </>
    
  )
}

export default App;
