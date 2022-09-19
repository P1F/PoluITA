function hideCadastro(username){
    document.getElementById('register-container').style.display = 'none'
    document.getElementById('login-container').style.display = 'none'
    document.getElementById('entrar').style.display = 'none'
    document.getElementById('cadastrar').style.display = 'none'
    document.getElementById('user-menu').style.display = 'block'
    document.getElementsByName('session-user')[0].textContent = username
}

function verAvaliacoes(){
    window.open('registros/' + document.getElementById('id-empresa').value.toString())
}

document.getElementById('entrar').addEventListener('click', function(){
    document.getElementById('register-container').style.display = 'none'
    var login = document.getElementById('login-container')
    if(login.style.display == 'block')
        login.style.display = 'none'
    else
        login.style.display = 'block'
})

document.getElementById('cadastrar').addEventListener('click', function(){
    document.getElementById('login-container').style.display = 'none'
    var login = document.getElementById('register-container')
    if(login.style.display == 'block')
        login.style.display = 'none'
    else
        login.style.display = 'block'
})

document.getElementById('user-menu').addEventListener('click', function(){
    var menu = document.getElementById('menu-container')
    if(menu.style.display == 'block')
        menu.style.display = 'none'
    else
        menu.style.display = 'block'
})

document.getElementById('menu-sair').addEventListener('click', function(){
    var xhr = new XMLHttpRequest;
    xhr.open('GET', 'registros/finalizarsessao')
    xhr.onreadystatechange = function () {
        if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            document.getElementById('entrar').style.display = 'block'
            document.getElementById('cadastrar').style.display = 'block'
            document.getElementById('user-menu').style.display = 'none'
            document.getElementById('menu-container').style.display = 'none'
        }
    };
    xhr.send()
})

document.getElementById('send-login').addEventListener('click', function(){
    document.getElementById('rotatelogin').style.display = 'block'

    document.getElementById('errouser-login').textContent = ''
    document.getElementById('errosenha-login').textContent = ''

    var formdata = new FormData(document.getElementById('login-box'))
    var xhr = new XMLHttpRequest;
    xhr.open('POST', 'registros/usuario/entrar')
    xhr.onreadystatechange = function () {
        if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText)
            if (!data['ok']){
                Object.keys(data).forEach((key, index)=>{
                    if (key!='ok')
                        document.getElementById('erro'+key).textContent = data[key]
                })
            }else{
                hideCadastro(data['user'])
            }
            document.getElementById('rotatelogin').style.display = 'none'
        }
    };
    xhr.send(formdata)

})

//TRIGGER DE ENVIAR DADOS DO REGISTER PARA O BANCO DE DADOS
document.getElementById('send-register').addEventListener('click', function(){
    //MOSTRA BOLINHA GIRANDO E LIMPA CAMPOS DE ERRO
    document.getElementById('rotateregister').style.display = 'block'
    document.getElementById('erronome').textContent = ''
    document.getElementById('erroemail').textContent = ''
    document.getElementById('errouser-register').textContent = ''
    document.getElementById('errosenha-register').textContent = ''
    document.getElementById('errorepetirsenha').textContent = ''

    //ADQUIRE OS DADOS DO FORMULARIO
    var formdata = new FormData(document.getElementById('register-box'))

    //VERIFICAÇÃO CLIENT SIDE
    if (formdata.get('senha-register') != formdata.get('repetirsenha')){
        document.getElementById('errorepetirsenha').textContent = 'As senhas devem ser idênticas.'
        document.getElementById('rotateregister').style.display = 'none'
        return
    }

    //REQUISIÇÃO AJAX
    var xhr = new XMLHttpRequest;
    xhr.open('POST', 'registros/usuario/registrar')
    xhr.onreadystatechange = function () {
        if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText)
            if (!data['ok']){
                Object.keys(data).forEach((key, index)=>{
                    if (key!='ok')
                        document.getElementById('erro'+key).textContent = data[key]
                })
            }else{
                hideCadastro(data['user'])
            }
            document.getElementById('rotateregister').style.display = 'none'
        }
    };
    xhr.send(formdata)

})

document.getElementById('send-avaliacao').addEventListener('click', function(){
    showLoader()
    document.getElementsByName('erronota')[0].textContent = ''
    document.getElementsByName('errocomentario')[0].textContent = ''
    document.getElementsByName('errologin')[0].textContent = ''

    var formdata = new FormData(document.getElementById('form-avaliacao'))

    var xhr = new XMLHttpRequest;
    xhr.open('POST', 'registros/generate-avaliacao')
    xhr.onreadystatechange = function () {
        if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var data = JSON.parse(xhr.responseText)
            console.log(data)
            if (!data['ok']){
                Object.keys(data).forEach((key, index)=>{
                    if (key!='ok')
                        document.getElementsByName('erro'+key)[0].textContent = data[key]
                })
                hideLoader()
            }else{
                hideModal()
                hideLoader()
                alert('Avaliação enviada com sucesso!')
            }
        }
    };
    xhr.send(formdata)

})
