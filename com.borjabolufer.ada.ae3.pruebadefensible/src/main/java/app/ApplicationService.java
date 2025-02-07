package app;

import java.util.List;

import com.borjabolufer.ada.ae3.pruebadefensible.dao.*;
import com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions.DatabaseException;

import entities.*;

public class ApplicationService {
	private CarDAO carDAO = CarDAO.getInstance();
	private PersonDAO personDAO = PersonDAO.getInstance();
	private PolicyDAO policyDAO = PolicyDAO.getInstance();
	private AccidentDAO accidentDAO = AccidentDAO.getInstance();

	// Métodos para gestionar personas
	public void addPerson(String driverID, String address, String name) throws DatabaseException {
		Person existingPerson = personDAO.findById(driverID);
		if (existingPerson != null) {
			throw new DatabaseException("Ya existe un conductor con ese id ");
		}
		Person person = new Person(driverID, address, name, null);
		personDAO.addPerson(person);
	}

	public List<Person> getAllPersons() throws DatabaseException {
		return personDAO.loadAllPersons();
	}

	// Métodos para gestionar coches
	public void addCar(String licenseID, String model, int year, String driverID) throws Exception {
		Car existingCar = carDAO.findById(licenseID);
		Person owner = personDAO.findById(driverID);
		if (owner == null) {
			throw new Exception("No se encontró la persona con ID: " + driverID);
		}
		if (existingCar != null) {
			throw new Exception("Ya existe un coche con ese id");
		}
		Car car = new Car(licenseID, model, year, owner, null, null);
		carDAO.addCar(car);
	}

	public List<Car> getAllCars() throws DatabaseException {
		return carDAO.loadAllCars();
	}

	public void addPolicy(String policyId, String licenseID) throws IllegalArgumentException, DatabaseException {
		// Validación del ID del coche
		if (licenseID == null || licenseID.trim().isEmpty()) {
			throw new IllegalArgumentException("El ID del coche no puede estar vacío");
		}

		try {
			// Convertir policyId vacío a null
			String cleanPolicyId = emptyToNull(policyId);

			// Si el policyId es null, generar un identificador único
			if (cleanPolicyId == null) {
				cleanPolicyId = generatePolicyId();
			}

			// Verificar si existe una póliza con el mismo ID
			Policy existingPolicy = policyDAO.findById(cleanPolicyId);
			if (existingPolicy != null) {
				throw new DatabaseException("Ya existe una póliza con ID: " + cleanPolicyId);
			}

			// Verificar si el coche existe
			Car car = carDAO.findById(licenseID.trim());
			if (car == null) {
				throw new DatabaseException("No existe un coche con ID: " + licenseID);
			}

			// Verificar si el coche ya tiene una póliza
			if (car.getPolicy() != null) {
				throw new DatabaseException("El coche ya tiene una póliza asociada");
			}

			// Crear y guardar la nueva póliza
			Policy newPolicy = new Policy(cleanPolicyId, car);
			car.setPolicy(newPolicy); // Relación bidireccional

			policyDAO.addPolicy(newPolicy);

		} catch (DatabaseException e) {
			throw new DatabaseException("Error al crear la póliza: " + e.getMessage(), e);
		}
	}

	public List<Policy> getAllPolicies() throws DatabaseException {
		return policyDAO.loadAllPolicies();
	}

	// Métodos para gestionar accidentes
	public void addAccident(String reportNumber, String location) throws DatabaseException {
		Accident accident = new Accident(reportNumber, location);
		accidentDAO.addAccident(accident);
	}

	public void addCarAccident(String licenseId, String reportNumber) throws DatabaseException {
		accidentDAO.addCarToAccident(licenseId, reportNumber);
	}

	public List<Accident> getAllAccidents() throws DatabaseException {
		return accidentDAO.loadAllAccidents();
	}

	private String generatePolicyId() {
		return "pol" + System.currentTimeMillis(); // Ejemplo: POL1675801234567
	}

	public boolean isDataInitialized() throws DatabaseException {
	    try {
	        List<Person> persons = personDAO.loadAllPersons();
	        return !persons.isEmpty();
	        
	    } catch (DatabaseException e) {
	        throw new DatabaseException("Error al verificar la inicialización de datos: " + e.getMessage(), e);
	    }
	}

	/**
	 * Convierte una cadena vacía o que solo contiene espacios en blanco a null. Si
	 * la cadena contiene caracteres no blancos, la devuelve limpia de espacios.
	 * 
	 * @param str la cadena a procesar
	 * @return null si la cadena es vacía o solo contiene espacios, la cadena limpia
	 *         de espacios en otro caso
	 */
	private String emptyToNull(String str) {
		if (str == null || str.trim().isEmpty()) {
			return null;
		}
		return str.trim();
	}
}