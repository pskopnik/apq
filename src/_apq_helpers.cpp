#include "binheap.hpp"

#include <cstddef>
#include <string>

template<class T>
class APQEntry {
public:
	std::size_t index;
	std::string key;
	double value;
	std::size_t change_ts;
	T data;

	APQEntry() {}
	APQEntry(std::size_t index, const std::string& key, double value, std::size_t change_ts, const T& data) : index(index), key(key), value(value), change_ts(change_ts), data(data) {}
	APQEntry(std::size_t index, const std::string& key, double value, std::size_t change_ts, T&& data) : index(index), key(key), value(value), change_ts(change_ts), data(data) {}

	void setIndex(std::size_t index) {
		this->index = index;
	}

	bool minHeapCompare(const APQEntry &other) const {
		if (value < other.value)
			return true;
		else if (value == other.value)
			return change_ts < other.change_ts;
		else
			return false;
	}

	bool maxHeapCompare(const APQEntry &other) const {
		if (value > other.value)
			return true;
		else if (value == other.value)
			return change_ts < other.change_ts;
		else
			return false;
	}
};

template<class T>
class PointerWrapper {
protected:
	T* e;

public:
	PointerWrapper(T* e) : e(e) {}
	PointerWrapper(T& e) : e(&e) {}

	bool maxHeapCompare(const PointerWrapper<T>& rhs) const {
		return e->maxHeapCompare(*rhs.e);
	}

	bool minHeapCompare(const PointerWrapper<T>& rhs) const {
		return e->minHeapCompare(*rhs.e);
	}

	void setIndex(std::size_t index) {
		e->setIndex(index);
	}

	T* get() {
		return e;
	}

	T& operator*() {
		return *e;
	}

	T* operator->() {
		return e;
	}
};


template<class T>
class DefaultSetIndex<PointerWrapper<T>> {
public:
	void operator()(PointerWrapper<T>& el, std::size_t index) const {
		el.setIndex(index);
	}
};
