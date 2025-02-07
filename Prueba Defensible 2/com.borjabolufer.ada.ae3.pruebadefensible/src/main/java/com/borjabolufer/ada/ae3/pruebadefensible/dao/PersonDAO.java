package com.borjabolufer.ada.ae3.pruebadefensible.dao;

import java.util.List;

import org.hibernate.Session;
import org.hibernate.Transaction;

import com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions.DatabaseException;

import entities.Person;
import jakarta.persistence.TypedQuery;
import util.HibernateSessionFactory;

public class PersonDAO {
private static PersonDAO instance = new PersonDAO ();
	
	public PersonDAO() {
	}

	public static PersonDAO  getInstance() {
		return instance;
	}



	public void addPerson(Person person) throws DatabaseException {
		Transaction tx = null;
		try {
			Session session = HibernateSessionFactory.getSessionSingleton();
			tx = session.beginTransaction();
			session.persist(person);
			tx.commit();
		} catch (Exception e) {
			if (tx != null) {
				tx.rollback();
			}else {
				throw new DatabaseException(e.getMessage(), e);
			}
		}
	}

	public Person findById(String id) {
		Session session = HibernateSessionFactory.getSessionSingleton();
		return session.get(Person.class, id);
	}

	public List<Person> loadAllPersons() throws DatabaseException {
		try {
			Session session = HibernateSessionFactory.getSessionSingleton();
			session.clear();
			TypedQuery<Person> query = session.createNativeQuery("SELECT * FROM Person_bb04", Person.class);
			List<Person> persons = query.getResultList();
			return persons;
		} catch (Exception e) {
			throw new DatabaseException(e.getMessage(), e);
		}
	}

}
