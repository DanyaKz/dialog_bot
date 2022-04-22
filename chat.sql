create database chat;
use chat;

create table actions(
	act_id int not null,
    act_name varchar(100),
    primary key(act_id)
);

create table users(
	user_id bigint not null unique,
	first_name varchar(250) not null,
	login varchar(50) not null,
	act int,
    busy boolean default true,
    primary key(user_id),
    foreign key(act) references actions(act_id)
);

create table hobbies(
	hobby_id serial , 
	user_id bigint not null,
    hobby text not null,
    primary key(hobby_id),
    foreign key(user_id) references users(user_id)
);

create table requests(
	req_id serial,
    req_time datetime not null,
    start_time datetime not null,
    end_time datetime not null,
    req_from bigint not null,
    req_to bigint not null,
    is_it_aproved boolean default false,
    is_it_end boolean,
	primary key(req_id),
    foreign key(req_from) references users(user_id),
    foreign key(req_to) references users(user_id)
);

create table messages(
	msg_id serial,
    f_user bigint,
    s_user bigint,
    m_time datetime,
    message text,
    stick text,
    primary key(msg_id),
    foreign key(f_user) references users(user_id),
    foreign key(s_user) references users(user_id)
);

create table queue(
	q_id serial,
    user_id bigint, 
    is_accepted boolean,
    primary key(q_id),
    foreign key (user_id) references users(user_id)
);

create table action_messages(
	a_m_id serial,
    user_id bigint, 
    act int,
    act_msg text,
    primary key(a_m_id),
    foreign key (user_id) references users(user_id),
    foreign key (act) references actions(act_id) 
);





