/*****************************************************************
 * file raisePythonException.cpp
 * Clement Chalumeau (SETI Institute) & Franck Marchis (Iris AO & SETI Institute)
 * date: Jun. 6, 2016
 *
 * Handle exceptions thrown by the dll: raise a python RuntimeError with a custom message
 *
 */

#include "Python.h"
#include <exception>
#include <string>
#include "irisao.mirrors.h"
#include <iostream>
#include <typeinfo>
#include <stdexcept>

#include "raisePythonException.h"


using namespace std;

// Define exceptions:


void raise_python_error() {
  try {
    if (PyErr_Occurred())
      ; // let the latest Python exn pass through and ignore the current one
    else
      throw;
  } catch (const std::bad_alloc& exn) {
    PyErr_SetString(PyExc_MemoryError, exn.what());
  } catch (const std::bad_cast& exn) {
    PyErr_SetString(PyExc_TypeError, exn.what());
  } catch (const std::domain_error& exn) {
    PyErr_SetString(PyExc_ValueError, exn.what());
  } catch (const std::invalid_argument& exn) {
    PyErr_SetString(PyExc_ValueError, exn.what());
  } catch (const std::ios_base::failure& exn) {
    PyErr_SetString(PyExc_IOError, exn.what());
  } catch (const std::out_of_range& exn) {
    PyErr_SetString(PyExc_IndexError, exn.what());
  } catch (const std::overflow_error& exn) {
    PyErr_SetString(PyExc_OverflowError, exn.what());
  } catch (const std::range_error& exn) {
    PyErr_SetString(PyExc_ArithmeticError, exn.what());
  } catch (const std::underflow_error& exn) {
    PyErr_SetString(PyExc_ArithmeticError, exn.what());
  } catch (const std::exception& exn) {
    PyErr_SetString(PyExc_RuntimeError, exn.what());
   // Define custom messages for our purposes
  } catch (Exception& exn ){
	  switch(exn){
	  	  case InsufficientMemory:
	  		PyErr_SetString(PyExc_RuntimeError, "Insufficient memory exception");
	  		break;
	  	  case InvalidArgument:
		  	PyErr_SetString(PyExc_RuntimeError, "Invalid function argument exception");
		  	break;
	  	  case InvalidDriverType:
     		PyErr_SetString(PyExc_RuntimeError, "Invalid driver type exception");
			break;
	  	  case InvalidMirrorType:
			PyErr_SetString(PyExc_RuntimeError, "Invalid mirror type exception");
			break;
	  	  case InvalidFileName:
			PyErr_SetString(PyExc_RuntimeError, "Invalid file name exception");
			break;
	  	  case MissingTag:
			PyErr_SetString(PyExc_RuntimeError, "Missing tag exception");
			break;
	  	  case NullPointer:
			PyErr_SetString(PyExc_RuntimeError, "Null pointer exception");
			break;
	  	  case InvalidConfiguration:
	  		PyErr_SetString(PyExc_RuntimeError, "Invalid configuration exception");
	  		break;
	  	  default:
	  		PyErr_SetString(PyExc_RuntimeError, "Unknown Iris AO exception");
	  		break;

	  }

  }
  catch (...)
  {
    PyErr_SetString(PyExc_RuntimeError, "Unknown exception");
  }
}
