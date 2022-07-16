import classes from './Login.module.css';

function LoginPage(){
    const REST_API_KEY = "52750403fc68645f09dd49b6b777a752"
    const REDIRECT_URI = "http://localhost:3000/home"

    const KAKAO_AUTH_URL = `https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=${REST_API_KEY}&redirect_uri=${REDIRECT_URI}`;

    return <> 
        <a href={KAKAO_AUTH_URL} >
            <img src="https://www.gb.go.kr/Main/Images/ko/member/certi_kakao_login.png"className={classes.btn}>

            </img>
        </a>
    
    </>
}

export default LoginPage;