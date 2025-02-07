package com.borjabolufer.ada.ae3.pruebadefensible.dao.exceptions;

public class DatabaseException extends Exception {

	/**
	 * Serial version UID
	 */
	private static final long serialVersionUID = 3046220019280940288L;

	public DatabaseException(String message, Throwable cause) {
		super(message, cause);
	}
	
	public DatabaseException(String message) {
		super(message);
	}
}
