package com.borjabolufer.ada.ae3.pruebadefensible.dao;

import java.util.List;

import org.hibernate.Session;
import org.hibernate.Transaction;

import com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions.DatabaseException;

import entities.Car;
import entities.Person;
import entities.Policy;
import jakarta.persistence.TypedQuery;
import util.HibernateSessionFactory;

public class PolicyDAO {
	
	private static PolicyDAO instance = new PolicyDAO();

	public PolicyDAO() {
		// TODO Auto-generated constructor stub
	}

	public static PolicyDAO getInstance() {
		return instance;
	}
	
	public void addPolicy(Policy policy) throws DatabaseException {
	    if (policy == null) {
	        throw new IllegalArgumentException("La póliza no puede ser null");
	    }

	    if (policy.getPolicyId() == null || policy.getPolicyId().trim().isEmpty()) {
	        throw new DatabaseException("El ID de la póliza debe ser asignado antes de persistir");
	    }

	    Transaction tx = null;
	    try {
	        Session session = HibernateSessionFactory.getSessionSingleton();
	        tx = session.beginTransaction();

	        // Verificar si ya existe una póliza con ese ID
	        Policy existingPolicy = session.get(Policy.class, policy.getPolicyId());
	        if (existingPolicy != null) {
	            throw new DatabaseException("Ya existe una póliza con ID: " + policy.getPolicyId());
	        }

	        // Verificar si el coche existe y no tiene ya una póliza
	        Car car = session.get(Car.class, policy.getCar().getLicenseID());
	        if (car == null) {
	            throw new DatabaseException("No existe el coche con ID: " + policy.getCar().getLicenseID());
	        }

	        session.persist(policy);
	        tx.commit();
	    } catch (Exception e) {
	        if (tx != null && tx.isActive()) {
	            tx.rollback();
	        }
	        throw new DatabaseException("Error al añadir la póliza: " + e.getMessage(), e);
	    }
	}

	public Policy findById(String id) {
		Session session = HibernateSessionFactory.getSessionSingleton();
		return session.get(Policy.class, id);
	}

	public List<Policy> loadAllPolicies() throws DatabaseException {
		try {
			Session session = HibernateSessionFactory.getSessionSingleton();
			session.clear();
			TypedQuery<Policy> query = session.createNativeQuery("SELECT * FROM Policy_bb04", Policy.class);
			List<Policy> policies = query.getResultList();
			return policies;
		} catch (Exception e) {
			throw new DatabaseException(e.getMessage(), e);
		}
	}


}
