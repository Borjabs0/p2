package entities;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinTable;
import jakarta.persistence.ManyToMany;
import jakarta.persistence.Table;
import jakarta.persistence.JoinColumn;

@Entity
@Table(name = "Accident_bb04")
public class Accident {
	@Id
	@Column(name = "REPORT_NUMBER", length = 50, nullable = false)
	private String ReportNumber;
	@Column(name = "LOCATION", length = 50)
	private String location;
	@ManyToMany
	@JoinTable(name = "participated_bb04", joinColumns = @JoinColumn(name = "REPORT_NUMBER"), inverseJoinColumns = @JoinColumn(name = "LICENSE_ID"))
	private Set<Car> cars = new HashSet<Car>();

	public Accident() {
	}

	public Accident(String reportNumber, String location) {
		super();
		this.ReportNumber = reportNumber;
		this.location = location;
		this.cars = new HashSet<Car>();
	}

	public Set<Car> getCars() {
        if (cars == null) {
            cars = new HashSet<>();
        }
        return cars;
    }

    public void setCars(Set<Car> cars) {
        this.cars = cars != null ? cars : new HashSet<>();
    }

	/**
	 * Metodo el cual añade un coche al accidente y establece la relación
	 * bidireccional. Este metodo mantiene la consistencia de la relación
	 * many-to-many entre Accident y Car, actualizando tanto la colección de coches
	 * del accidente como la colección de accidentes del coche
	 * 
	 * @param car El objeto car se va a añadir al accidente
	 */
	public void addCar(Car car) {
		this.cars.add(car);
		car.getAccidents().add(this);
	}

	/**
	 * Elimina un coche del accidente y rompe la relación bidireccional. Este método
	 * mantiene la consistencia de la relación many-to-many entre Accident y Car,
	 * eliminando el coche de la colección de coches del accidente y el accidente de
	 * la colección de accidentes del coche.
	 *
	 * @param car El objeto car se va a eliminar del accidente
	 */
	public void removeCar(Car car) {
		this.cars.remove(car);
		car.getAccidents().remove(this);
	}

	public String getReportNumber() {
		return ReportNumber;
	}

	public void setReportNumber(String reportNumber) {
		ReportNumber = reportNumber;
	}

	public String getLocation() {
		return location;
	}

	public void setLocation(String location) {
		this.location = location;
	}

	@Override
	public String toString() {
		return "Accident [ReportNumber=" + ReportNumber + ", location=" + location + "]";
	}

	@Override
	public int hashCode() {
		return Objects.hash(ReportNumber, location);
	}

	@Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Accident other = (Accident) obj;
        return Objects.equals(ReportNumber, other.ReportNumber);
    }

}
