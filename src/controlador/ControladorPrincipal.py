from src.modelo.vo.LoginVo import LoginVo


class COntroladorPrincipal:
    def __init__(self, ref_vista, ref_modelo):
        self.vista = ref_vista
        self._modelo = ref_modelo
        
    def ventanaIniciarSesión(self):
        self._vista.show()
        self._modelo.pruebaselect()

    def comprobarLogin(self, nombre, passw):
        login = LoginVo(nombre, passw)
        resultado = self._modelo.consultarLogin(login) 

        if resultado == None:
            print("no existe")
            self._vista.lanzarAvisoLogin()        
        else:
            self._vista.close()
            


    
