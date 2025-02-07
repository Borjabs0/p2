package com.borjabolufer.ada.ae3.pruebadefensible.dao;

import java.util.Collection;
import java.util.HashSet;
import java.util.List;

import org.hibernate.Session;

import entities.Accident;
import entities.Car;
import entities.Person;
import jakarta.persistence.TypedQuery;

import org.hibernate.Transaction;

import com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions.DatabaseException;

import util.HibernateSessionFactory;

public class AccidentDAO {

	private static AccidentDAO instance = new AccidentDAO();

	public AccidentDAO() {
	}

	public static AccidentDAO getInstance() {
		return instance;
	}

	public void addAccident(Accident accident) throws DatabaseException {
		Transaction tx = null;
		try {
			Session session = HibernateSessionFactory.getSessionSingleton();
			tx = session.beginTransaction();
			session.persist(accident);
			tx.commit();
		} catch (Exception e) {
			if (tx != null) {
				tx.rollback();
			} else {
				throw new DatabaseException(e.getMessage(), e);
			}
		}
	}

	public void addCarToAccident(String licenseId, String reportNumber) throws DatabaseException {
	    Session session = null;
	    Transaction tx = null;
	    try {
	        session = HibernateSessionFactory.getSessionSingleton();
	        tx = session.beginTransaction();

	        // Verificar explícitamente si existen
	        Accident accident = session.get(Accident.class, reportNumber);
	        Car car = session.get(Car.class, licenseId);

	        if (accident == null) {
	            throw new DatabaseException("Accidente no encontrado: " + reportNumber);
	        }
	        if (car == null) {
	            throw new DatabaseException("Coche no encontrado: " + licenseId);
	        }

	        // Inicializar colecciones si son null
	        if (accident.getCars() == null) {
	            accident.setCars(new HashSet<>());
	        }
	        if (car.getAccidents() == null) {
	            car.setAccidents(new HashSet<>());
	        }

	        // Establecer la relación bidireccional
	        accident.getCars().add(car);
	        car.getAccidents().add(accident);

	        // Actualizar las entidades
	        session.merge(accident);
	        session.merge(car);

	        tx.commit();
	    } catch (Exception e) {
	        if (tx != null && tx.isActive()) {
	            tx.rollback();
	        }
	        throw new DatabaseException("Error al añadir el coche al accidente: " + e.getMessage(), e);
	    }
	}

	public Accident findById(String id) {
		Session session = HibernateSessionFactory.getSessionSingleton();
		return session.get(Accident.class, id);
	}

	public List<Accident> loadAllAccidents() throws DatabaseException {
		try {
			Session session = HibernateSessionFactory.getSessionSingleton();
			session.clear();
			TypedQuery<Accident> query = session.createNativeQuery("SELECT * FROM Accident_bb04", Accident.class);
			List<Accident> accidents = query.getResultList();
			return accidents;
		} catch (Exception e) {
			throw new DatabaseException(e.getMessage(), e);
		}
	}

}
