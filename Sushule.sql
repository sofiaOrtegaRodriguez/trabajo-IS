
USE SushUle;

CREATE TABLE EMPLEADOS (





	IDEmp int not null identity (1,1)

		constraint PK_Empleados primary key,



	Emp_SSN varchar(11) not null

		constraint UQ_SSN UNIQUE

		constraint CK_Employees_Emp_SSN CHECK (Emp_SSN LIKE '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),



	Emp_User varchar(50) not null

		constraint UQ_Emp_User UNIQUE,



	Emp_Correo varchar(100) not null

		constraint UQ_Emp_Correo UNIQUE

		constraint CK_Empleados_Correo CHECK (Emp_Correo LIKE '%@%'),



	Emp_Contrasena varchar(50) not null,



	Emp_Tipo varchar(20) not null

		constraint CK_Empleados_Tipo CHECK (Emp_Tipo IN ('GERENTE', 'ADMINISTRADOR', 'CAJERO', 'COCINA'))



);



CREATE TABLE CAJEROS (
	ID_Cajero int not null
		constraint PK_Cajeros primary key
		constraint FK_Emp_Cajero_IDEmp foreign key references EMPLEADOS(IDEmp)
);



CREATE TABLE CLIENTES(

    IdCli int not null identity (1,1)

        constraint PK_Clientes primary key,

    Nombre nvarchar(50) not null

        constraint UQ_Clientes_Nombre UNIQUE,

    Correo nvarchar(50) not null

        constraint UQ_Clientes_Correo UNIQUE

        constraint CK_Clientes_Correo CHECK (Correo LIKE '%@%'),

    Contrasena nvarchar(50) not null,

    Puntos int not null default 0

        constraint CK_Clientes_Puntos_MayorCero CHECK (Puntos >= 0),

    FechaCuenta date not null

        constraint CK_Clientes_FechaCuenta CHECK (FechaCuenta <= getdate()),



);



CREATE TABLE PRODUCTOS(

    Nombre nvarchar(100) not null

        constraint PK_Productos primary key,

    Precio smallmoney not null

        constraint CK_Productos_Precio_MayorCero CHECK (Precio > 0),

    Ingredientes nvarchar(1000) not null,

    Disponible char(1) not null

        constraint CK_Productos_Disponible CHECK (Disponible IN ('Y', 'N')),

    Stock int not null default (0)

        constraint CK_Productos_Stock_MayorCero CHECK (Stock > 0),

);



CREATE TABLE PROMOCIONES (

	IDProm int identity(1,1)

		constraint PK_IDProm primary key,

	Descuento tinyint not null

		CHECK (Descuento BETWEEN 0 AND 100),

	FechaInicio date not null,

	FechaFin date not null,

		CHECK (FechaFin > FechaInicio)

);



CREATE TABLE PEDIDOS(

	IDPed int identity(1,1)

		constraint PK_IDPed primary key,

	PrecioTotal float not null,

	Hora date not null,

	Estado varchar(20) not null default 'PENDIENTE'

		CHECK (Estado IN ('PENDIENTE', 'PAGADO', 'PREPARANDO', 'LISTO')),

	IDCli int constraint FK_PEDIDOS_FIDCli foreign key references CLIENTES(IDCli),

	IDCaj int constraint FK_PEDIDOS_FIDCaj foreign key references CAJEROS(ID_Cajero),

		CHECK (IDCli IS NOT NULL OR IDCaj IS NOT NULL)

);



CREATE TABLE PRODPED(

	NombreProd nvarchar(100) constraint FK_PRODPED_FNombreProd foreign key references PRODUCTOS(Nombre),

	IDPed int constraint FK_PRODPED_FIDPed foreign key references PEDIDOS(IDPed),

	Cantidad tinyint not null default 1,

		constraint PK_PRODPED PRIMARY KEY (NombreProd, IDPed)

);



CREATE TABLE PRODPROM(

	NombreProd nvarchar(100) constraint FK_PRODPROM_FNombreProd foreign key references PRODUCTOS(Nombre),

	IDProm int constraint FK_PRODPED_FIDProm foreign key references PROMOCIONES(IDProm),

		constraint PK_PRODPROM PRIMARY KEY (NombreProd, IDProm)

);
