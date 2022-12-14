drop table consumption;
drop table devices;
drop table users;
drop table addresses;
drop table days;

create table users(
	ID serial unique,
	username varchar(30),
	password varchar(32),
	role int DEFAULT 0,
	primary key(ID)
);

create table addresses(
	ID serial unique,
	country varchar(30),
	city varchar(30)
);

create table devices(
	ID serial unique,
	description text,
	address_id int,
	max_hourly_consumption int,
	owner_id int,
	primary key(ID),
	foreign key (address_id) references addresses(ID),
	foreign key (owner_id) references users(ID)
);

create table consumption(
	device_id int,
	my_timestamp timestamp default NOW(),
	energy_consumption int,
	foreign key (device_id) references devices(ID)
);

create table days(
	year int,
	month VARCHAR(10),
	days_in_month int
);

insert into days values(2022, 'January', 31);
insert into days values(2022, 'February', 28);
insert into days values(2022, 'March', 31);
insert into days values(2022, 'April', 30);
insert into days values(2022, 'May', 31);
insert into days values(2022, 'June', 30);
insert into days values(2022, 'July', 31);
insert into days values(2022, 'August', 31);
insert into days values(2022, 'September', 30);
insert into days values(2022, 'October', 31);
insert into days values(2022, 'November', 30);
insert into days values(2022, 'December', 31);
insert into days values(2023, 'January', 31);
insert into days values(2023, 'February', 28);
insert into days values(2023, 'March', 31);


insert into users(username, password, role)
	values('Lungoci Luca', 'ff377aff39a9345a9cca803fb5c5c081', 1);
insert into users(username, password, role)
	values('Rus Iulia', '48b08b5caf405b5e2859e0dbec4a6a4d', 0);
insert into users(username, password, role)
	values('Mihai Alexandru', 'fe86160cf6aad05862000f43e16f0194', 0);
insert into users(username, password, role)
	values('test', '098f6bcd4621d373cade4e832627b4f6', 0);
	
insert into addresses(country, city) values('Romania', 'Cluj-Napoca');
insert into addresses(country, city) values('Romania', 'Bucharest');

insert into devices(description, address_id, max_hourly_consumption, owner_id) 
	values ('This devices is yellow.', 1, 100, 1);
insert into devices(description, address_id, max_hourly_consumption, owner_id) 
	values ('Old device.', 1, 343, 1);
insert into devices(description, address_id, max_hourly_consumption, owner_id) 
	values ('Device needs checking at the begining of every month.', 1, 67, 2);
insert into devices(description, address_id, max_hourly_consumption, owner_id) 
	values ('Test device 1.', 2, 67, 4);
insert into devices(description, address_id, max_hourly_consumption, owner_id) 
	values ('Test device 2.', 2, 67, 4);
insert into devices(description, address_id, max_hourly_consumption, owner_id) 
	values ('Test device 3.', 2, 67, 4);
insert into devices(description, address_id, max_hourly_consumption, owner_id) 
	values ('Test device 4.', 2, 67, 4);

	
insert into consumption values(4, '2022-10-08 17:05:00', 11);
insert into consumption values(5, '2022-10-08 17:05:00', 10);
insert into consumption values(6, '2022-10-08 17:05:00', 9);
insert into consumption values(7, '2022-10-08 17:05:00', 100);
insert into consumption values(7, '2022-10-08 17:05:00', 1);
insert into consumption values(7, '2022-10-08 17:05:00', 10);
insert into consumption(device_id, energy_consumption) values(2, 12);
insert into consumption(device_id, energy_consumption) values(3, 63);