import {Link} from 'react-router-dom';


import classes from './NavBar.module.css';

function NavBar(){
    

    return (
        <div className={classes.NavBar}>
            <ul className={classes.list}>
                <li>
                    <Link to ='/home'> Home </Link>
                </li>

                <li>
                    <Link to ='/home/chart'> chart </Link>
                </li>
                    
                <li>
                    <Link to ='/home/balance'> balance </Link>    
                </li>
    
                <li>
                    <Link to ='/home/popol'> popol </Link>
                </li>

                <li>
                    <Link to ='/home/search'> search🔎 </Link>
                </li>
            </ul>

        </div>


    )
}

export default NavBar;