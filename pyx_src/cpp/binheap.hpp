#ifndef BIN_HEAP_H
#define BIN_HEAP_H

#include <cstddef>
#include <algorithm>
#include <functional>
#include <iterator>
#include <memory>
#include <type_traits>
#include <vector>

#include <cassert>

template<
	class T = void
>
class DefaultSetIndex {
public:
	void operator()(T& el, std::size_t index) const {
		(void)el;
		(void)index;
	}
};

template<
	class T,
	class Container = std::vector<T>,
	class Compare = std::less<typename Container::value_type>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
class BinHeap;

template<class T>
class MinHeapCompare {
public:
	bool operator()(const T& lhs, const T& rhs) const {
		return lhs.minHeapCompare(rhs);
	}
};

template<class T>
class MaxHeapCompare {
public:
	bool operator()(const T& lhs, const T& rhs) const {
		return lhs.maxHeapCompare(rhs);
	}
};

template<
	class T,
	class Container = std::vector<T>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
using MinBinHeap = BinHeap<T, Container, MinHeapCompare<T>, SetIndex>;

template<
	class T,
	class Container = std::vector<T>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
using MaxBinHeap = BinHeap<T, Container, MaxHeapCompare<T>, SetIndex>;

template<
	class T,
	class Container, // default value in forward declaration above
	class Compare, // default value in forward declaration above
	class SetIndex // default value in forward declaration above
>
class BinHeap {
public:
	using container_type = Container;
	using value_compare = Compare;
	using value_set_index = SetIndex;
	using instantiated_heap_type = BinHeap<T, container_type, value_compare, value_set_index>;

	using value_type = typename Container::value_type;
	using size_type = typename Container::size_type;
	using difference_type = typename Container::difference_type;
	using reference = typename Container::reference;
	using const_reference = typename Container::const_reference;

	using iterator = typename Container::iterator;
	using const_iterator = typename Container::const_iterator;

protected:
	class _OrderedIteratorEntry {
	protected:
		const instantiated_heap_type* valueHeap;
		size_type ind;

	public:
		bool minHeapCompare(const _OrderedIteratorEntry& other) const {
			return valueHeap->compare((*valueHeap)[ind], (*valueHeap)[other.ind]);
		}

		size_type getInd() const {
			return ind;
		}

		_OrderedIteratorEntry(const instantiated_heap_type* valueHeap, size_type ind) : valueHeap(valueHeap), ind(ind) {}
	};

public:
	template<bool Const>
	class _OrderedIterator {
	public:
		using iterator_category = std::forward_iterator_tag;
		using value_type = instantiated_heap_type::value_type;
		using difference_type = std::ptrdiff_t;
		using reference = typename std::conditional_t<Const, const value_type &, value_type &>;
		using pointer = typename std::conditional_t<Const, const value_type *, value_type *>;

		using referenced_heap_type = typename std::conditional_t<Const, const instantiated_heap_type, instantiated_heap_type>;
		using heap_pointer_type = referenced_heap_type*;

	protected:
		MinBinHeap<_OrderedIteratorEntry> entryHeap;
		heap_pointer_type valueHeap;

		// Grant friend access to const iterators from non-const iterators:
		template<bool Const1>
		friend class _OrderedIterator;

	public:
		/*
		 * Definitions satisfying the LegacyIterator requirement.
		 *
		 * https://en.cppreference.com/w/cpp/named_req/Iterator
		 */

		reference operator*() const { return (*valueHeap)[entryHeap.top().getInd()]; }

		_OrderedIterator<Const>& operator++() {
			size_type ind = entryHeap.top().getInd();
			const size_type leftChildInd = 2 * ind + 1;
			const size_type rightChildInd = 2 * ind + 2;

			entryHeap.pop();

			if (leftChildInd < valueHeap->size())
				entryHeap.emplace(valueHeap, leftChildInd);
			if (rightChildInd < valueHeap->size())
				entryHeap.emplace(valueHeap, rightChildInd);

			return *this;
		}

		/*
		 * Definitions satisfying the EqualityComparable requirement.
		 *
		 * https://en.cppreference.com/w/cpp/named_req/EqualityComparable
		 */

		friend bool operator==(const _OrderedIterator<Const>& lhs, const _OrderedIterator<Const>& rhs) {
			if (lhs.valueHeap != rhs.valueHeap)
				return false;

			if (lhs.entryHeap.size() == 0 || rhs.entryHeap.size() == 0)
				return lhs.entryHeap.size() == 0 && rhs.entryHeap.size() == 0;

			return lhs.entryHeap.top().getInd() == rhs.entryHeap.top().getInd();
		}

		/*
		 * Further definitions satisfying the LegacyInputIterator requirement.
		 *
		 * https://en.cppreference.com/w/cpp/named_req/InputIterator
		 */

		pointer operator->() const { return &(**this); }

		_OrderedIterator<Const> operator++(int) {
			_OrderedIterator<Const> tmpIt(*this);
			++(*this);
			return tmpIt;
		}

		friend bool operator!=(const _OrderedIterator<Const>& lhs, const _OrderedIterator<Const>& rhs) {
			return !(lhs == rhs);
		}

		/*
		 * Further definitions satisfying the LegacyForwardIterator requirement.
		 *
		 * https://en.cppreference.com/w/cpp/named_req/ForwardIterator
		 */

		_OrderedIterator() {}

		_OrderedIterator(referenced_heap_type* valueHeap) : valueHeap(valueHeap) {}
		_OrderedIterator(referenced_heap_type* valueHeap, int) : valueHeap(valueHeap) {
			if (valueHeap->size() > 0)
				entryHeap.emplace(valueHeap, 0);
		}

		/**
		 * Conversion operator, converts non-const into const iterator.
		 */
		operator _OrderedIterator<true>() const {
			_OrderedIterator<true> constIt(valueHeap);
			constIt.entryHeap = entryHeap;
			return constIt;
		}
	};

	using ordered_iterator = _OrderedIterator<false>;
	using const_ordered_iterator = _OrderedIterator<true>;

	template <bool Const>
	class _OrderedIterable {
		using iterator_type = std::conditional_t<Const, const_ordered_iterator, ordered_iterator>;
		using const_iterator_type = const_ordered_iterator;
		using heap_reference_type = typename std::conditional_t<Const, instantiated_heap_type const &, instantiated_heap_type &>;

		heap_reference_type valueHeap;

	public:
		_OrderedIterable(heap_reference_type valueHeap) : valueHeap(valueHeap) {}

		iterator_type begin() const { return iterator_type(&valueHeap, 0); }
		iterator_type end() const { return iterator_type(&valueHeap); }
		const_iterator_type cbegin() const { return const_iterator_type(&valueHeap, 0); }
		const_iterator_type cend() const { return const_iterator_type(&valueHeap); }
	};

	using ordered_iterable = _OrderedIterable<false>;
	using const_ordered_iterable  = _OrderedIterable<true>;

protected:
	Container container;
	Compare compare;
	SetIndex setIndex;

	void siftUp(size_type holeInd, size_type startInd, value_type&& value) {
		/*
		 * container is a heap at all indices >= startInd, except possibly
		 * for holeInd. startInd <= holeInd or no work is done. value is
		 * presumed at holeInd and must be less or equal to any of the holeInd
		 * children (simple case: leaf).
		 *
		 * Restore the heap invariant by moving value to the right position by
		 * moving up the hole until parent is <= value.
		 */

		assert(holeInd >= 0);
		assert(startInd >= 0);
		assert(holeInd < container.size());
		assert(startInd <= holeInd);
		assert(container.size() <= holeInd * 2 + 1 || !compare(container[holeInd * 2 + 1], value));
		assert(container.size() <= holeInd * 2 + 2 || !compare(container[holeInd * 2 + 2], value));
		assert(isHeap(container.cbegin(), container.cbegin() + startInd, container.cbegin() + holeInd));
		assert(container.size() <= holeInd * 2 + 1 || isHeap(container.cbegin(), container.cbegin() + holeInd * 2 + 1, container.cend()));
		assert(container.size() <= holeInd * 2 + 2 || isHeap(container.cbegin(), container.cbegin() + holeInd * 2 + 2, container.cend()));

		while (holeInd > startInd) {
			const size_type parentPos = (holeInd - 1) / 2;
			if (!compare(value, container[parentPos]))
				// parent <= value
				break;

			container[holeInd] = std::move(container[parentPos]);
			setIndex(container[holeInd], holeInd);
			holeInd = parentPos;
		}

		container[holeInd] = std::move(value);
		setIndex(container[holeInd], holeInd);
	}

	void siftDown(size_type holeInd, value_type&& value) {
		/*
		 * container is a heap at all indices of the sub-tree (transitive
		 * children) of holeInd except possibly at holeInd. value is presumed
		 * at holeInd.
		 *
		 * Restore the heap invariant by moving down the hole by bubbling up
		 * the smaller child starting at holeInd (recursively until reaching a
		 * leaf), then using siftUp to move value to the right place.
		 */

		assert(holeInd >= 0);
		assert(holeInd < container.size());
		assert(container.size() <= holeInd * 2 + 1 || isHeap(container.cbegin(), container.cbegin() + holeInd * 2 + 1, container.cend()));
		assert(container.size() <= holeInd * 2 + 2 || isHeap(container.cbegin(), container.cbegin() + holeInd * 2 + 2, container.cend()));

		const size_type len = container.size();
		const size_type limit = (len - 1) / 2; // first index that does not have two children
		const size_type startInd = holeInd;

		// while the hole has two children...
		while (holeInd < limit) {
			// ... move up its smaller child

			size_type childInd = 2 * holeInd + 1; // left child
			if (!compare(container[childInd], container[childInd + 1])) {
				// right child <= left child
				childInd++; // set childInd to index of right child
			}

			container[holeInd] = std::move(container[childInd]);
			setIndex(container[holeInd], holeInd);
			holeInd = childInd;
		}

		// if the container has a lone left child and the hole is at this child's parent index...
		if ((len & 1) == 0 && holeInd == (len - 2) / 2) {
			// ... move up the lone left child
			container[holeInd] = std::move(container[len - 1]);
			setIndex(container[holeInd], holeInd);
			holeInd = len - 1;
		}

		siftUp(holeInd, startInd, std::move(value));
	}

	void buildHeap() {
		if (container.size() > 1) {
			// starts at the index i with at least one child; iPlusOne = i + 1
			for (size_type iPlusOne = (container.size() - 2) / 2 + 1; iPlusOne > 0; --iPlusOne) {
				const size_type i = iPlusOne - 1;
				value_type value = std::move(container[i]);
				siftDown(i, std::move(value));
			}
		} else if (container.size() == 1) {
			setIndex(container[0], 0);
		}

		// set indices for values not explicitly sifted down
		for (size_type i = (container.size() - 2) / 2 + 1; i < container.size(); ++i) {
			setIndex(container[i], i);
		}
	}

	void fixPushed() {
		value_type val = std::move(container.back());
		siftUp(container.size() - 1, 0, std::move(val));
	}

	void fixValue(size_type ind, value_type&& value) {
		const size_type len = container.size();
		if ((
				2 * ind + 1 < len && compare(container[2 * ind + 1], value) // left child < value?
			) || (
				2 * ind + 2 < len && compare(container[2 * ind + 2], value) // right child < value?
		))
			siftDown(ind, std::move(value));
		else
			siftUp(ind, 0, std::move(value));
	}

	bool isHeap(
		typename container_type::const_iterator beginIt,
		typename container_type::const_iterator startIt,
		typename container_type::const_iterator endIt
	) const {
		const auto len = std::distance(beginIt, endIt);

		for (auto it = startIt; it != endIt; ++it) {
			const auto ind = std::distance(beginIt, it);

			const auto leftChildInd = 2 * ind + 1;
			const auto rightChildInd = leftChildInd + 1;
			if (leftChildInd < len && compare(*(beginIt + leftChildInd), *it))
					return false;
			if (rightChildInd < len && compare(*(beginIt + rightChildInd), *it))
					return false;
		}
		return true;
	}

	template<
		class T1,
		class Container1,
		class Compare1,
		class SetIndex1
	>
	friend class BinHeapVerifier;

public:
	BinHeap() : BinHeap(Compare(), SetIndex(), Container()) {}
	BinHeap(const Compare& comp, const SetIndex& setInd, const Container& cont) : container(cont), compare(comp), setIndex(setInd) {
		buildHeap();
	}
	BinHeap(const Compare& comp, const SetIndex& setInd, Container&& cont) : container(cont), compare(comp), setIndex(setInd) {
		buildHeap();
	}
	template<class InputIt>
	BinHeap(InputIt first, InputIt last, const Compare& comp, const SetIndex& setInd, const Container& cont) : container(cont), compare(comp), setIndex(setInd) {
		container.insert(container.end(), first, last);
		buildHeap();
	}
	template<class InputIt>
	BinHeap(InputIt first, InputIt last, const Compare& comp = Compare(), const SetIndex& setInd = SetIndex(), Container&& cont = Container()) : container(cont), compare(comp), setIndex(setInd) {
		container.insert(container.end(), first, last);
		buildHeap();
	}

	void clear() {
		container.clear();
	}

	void push(const value_type& value) {
		container.push_back(value);
		fixPushed();
	}
	void push(value_type&& value) {
		container.push_back(std::move(value));
		fixPushed();
	}

	template<class... Args>
	void emplace(Args&&... args) {
		container.emplace_back(std::forward<Args>(args)...);
		fixPushed();
	}

	void fix(size_type ind) {
		value_type value = std::move(container[ind]);
		fixValue(ind, std::move(value));
	}
	void fix(iterator it) {
		fix(it - begin());
	}
	void fix(const_iterator it) {
		fix(it - cbegin());
	}

	void remove(size_type ind) {
		value_type value = std::move(container.back());
		container.pop_back();
		if (ind < container.size())
			fixValue(ind, std::move(value));
	}
	void remove(iterator it) {
		remove(it - begin());
	}
	void remove(const_iterator it) {
		remove(it - cbegin());
	}

	void pop() {
		value_type value = std::move(container.back());
		container.pop_back();
		if (0 < container.size())
			siftDown(0, std::move(value));
	}

	bool empty() const {
		return container.empty();
	}
	size_type size() const {
		return container.size();
	}

	reference top() {
		return container.front();
	}

	const_reference top() const {
		return container.front();
	}

	reference operator[](size_type ind) {
		return container[ind];
	}
	const_reference operator[](size_type ind) const {
		return container[ind];
	}

	iterator begin() {
		return container.begin();
	}
	iterator end() {
		return container.end();
	}

	const_iterator begin() const {
		return container.begin();
	}
	const_iterator end() const {
		return container.end();
	}

	const_iterator cbegin() const {
		return container.cbegin();
	}
	const_iterator cend() const {
		return container.cend();
	}

	ordered_iterable orderedIterable() { return ordered_iterable(*this); }
	const_ordered_iterable orderedIterable() const { return const_ordered_iterable(*this); }
};

template<
	class T,
	class Container = std::vector<T>,
	class Compare = std::less<typename Container::value_type>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
class BinHeapVerifier {
public:
	using heap_type = BinHeap<T, Container, Compare, SetIndex>;

private:
	heap_type& heap;

public:
	BinHeapVerifier(heap_type& heap) : heap(heap) {}
	bool verify() const {
		return heap.isHeap(heap.container.cbegin(), heap.container.cbegin(), heap.container.cend());
	}
};

template<
	class T,
	class V = double,
	bool ChangeTSTracking = true,
	class SetIndex = DefaultSetIndex<T>
> class StandardEntry {
protected:
	using _full_ts_type = std::size_t;
	using _empty_ts_type = class{};

public:
	using value_type = V;
	using data_type = T;
	using ts_type = typename std::conditional<ChangeTSTracking, _full_ts_type, _empty_ts_type>::type;
	using entry_type = StandardEntry<T, V, ChangeTSTracking, SetIndex>;

protected:
	SetIndex _setIndex;

	V value;
	ts_type changeTS;
	T data;

public:
	StandardEntry() {}
	StandardEntry(V value, const T& data) : value(value), data(data) {}
	StandardEntry(V value, T&& data) : value(value), data(data) {}
	StandardEntry(V value, const T& data, ts_type changeTS) : value(value), changeTS(changeTS), data(data) {}
	StandardEntry(V value, T&& data, ts_type changeTS) : value(value), changeTS(changeTS), data(data) {}

	void setIndex(std::size_t index) {
		_setIndex(data, index);
	}

	void set(V val, const T& d) {
		value = val;
		data = d;
	}
	void set(V val, T&& d) {
		value = val;
		data = std::move(d);
	}
	void set(V val, const T& d, ts_type ts) {
		value = val;
		data = d;
		changeTS = ts;
	}
	void set(V val, T&& d, ts_type ts) {
		value = val;
		data = std::move(d);
		changeTS = ts;
	}

	V getValue() const {
		return value;
	}
	void setValue(V val) {
		value = val;
	}
	void setValue(V val, ts_type ts) {
		value = val;
		changeTS = ts;
	}

	ts_type getChangeTS() const {
		return changeTS;
	}
	void setChangeTS(ts_type ts) {
		changeTS = ts;
	}

	T& getData() {
		return data;
	}
	void setData(const T& d) {
		data = d;
	}
	void setData(T&& d) {
		data = std::move(d);
	}
	void setData(const T& d, ts_type ts) {
		data = d;
		changeTS = ts;
	}
	void setData(T&& d, ts_type ts) {
		data = std::move(d);
		changeTS = ts;
	}

	bool minHeapCompare(const entry_type &other) const {
		return _minHeapCompare(other, ts_type());
	}

	bool maxHeapCompare(const entry_type &other) const {
		return _maxHeapCompare(other, ts_type());
	}

protected:
	bool _minHeapCompare(const entry_type &other, _full_ts_type) const {
		if (value < other.value)
			return true;
		else if (value == other.value)
			return changeTS < other.changeTS;
		else
			return false;
	}

	bool _minHeapCompare(const entry_type &other, _empty_ts_type) const {
		return value < other.value;
	}

	bool _maxHeapCompare(const entry_type &other, _full_ts_type) const {
		if (value > other.value)
			return true;
		else if (value == other.value)
			return changeTS < other.changeTS;
		else
			return false;
	}

	bool _maxHeapCompare(const entry_type &other, _empty_ts_type) const {
		return value > other.value;
	}
};

template<
	class T,
	class V,
	bool ChangeTSTracking,
	class SetIndex
>
class DefaultSetIndex<StandardEntry<T, V, ChangeTSTracking, SetIndex>> {
public:
	void operator()(StandardEntry<T, V, ChangeTSTracking, SetIndex>& e, std::size_t index) const {
		e.setIndex(index);
	}
};

template<class T>
class BinHeapInterface {
public:
	// TODO this helper definition avoids having to define abstract iterators.
	// However, only std::vector<T> is possible as the BinHeap container.
	using container_type = typename std::vector<T>;

	using value_type = typename container_type::value_type;
	using size_type = typename container_type::size_type;
	using difference_type = typename container_type::difference_type;
	using reference = typename container_type::reference;
	using const_reference = typename container_type::const_reference;

	using iterator = typename container_type::iterator;
	using const_iterator = typename container_type::const_iterator;

	template<bool Const>
	class _OrderedIterator {
	public:
		using iterator_category = std::forward_iterator_tag;
		using value_type = BinHeapInterface<T>::value_type;
		using difference_type = std::ptrdiff_t;
		using reference = typename std::conditional_t<Const, value_type const &, value_type &>;
		using pointer = typename std::conditional_t<Const, value_type const *, value_type *>;

		virtual ~_OrderedIterator() {}

		virtual reference operator*() const = 0;
		virtual pointer operator->() const = 0;
		virtual _OrderedIterator<Const>& operator++() = 0;
		virtual std::unique_ptr<_OrderedIterator<Const>> operator++(int) = 0;
		virtual bool operator==(const _OrderedIterator<Const>& other) const = 0;
		virtual bool operator!=(const _OrderedIterator<Const>& other) const = 0;

		virtual std::unique_ptr<_OrderedIterator<Const>> clone() const = 0;

		virtual operator std::unique_ptr<_OrderedIterator<true>>() const = 0;
	};

	using ordered_iterator = _OrderedIterator<false>;
	using const_ordered_iterator = _OrderedIterator<true>;

	template<bool Const>
	class _OrderedIterable {
	public:
		using iterator_type = std::conditional_t<Const, const_ordered_iterator, ordered_iterator>;
		using const_iterator_type = const_ordered_iterator;

		virtual ~_OrderedIterable() {}

		virtual std::unique_ptr<iterator_type> begin() const = 0;
		virtual std::unique_ptr<iterator_type> end() const = 0;
		virtual std::unique_ptr<const_iterator_type> cbegin() const = 0;
		virtual std::unique_ptr<const_iterator_type> cend() const = 0;
	};

	using ordered_iterable = _OrderedIterable<false>;
	using const_ordered_iterable  = _OrderedIterable<true>;

	virtual ~BinHeapInterface() {};

	virtual void clear() = 0;

	virtual void push(const value_type& value) = 0;
	virtual void push(value_type&& value) = 0;

	// template<class... Args>
	// virtual void emplace(Args&&... args) = 0;

	virtual void fix(size_type ind) = 0;
	virtual void fix(iterator it) = 0;
	virtual void fix(const_iterator it) = 0;

	virtual void remove(size_type ind) = 0;
	virtual void remove(iterator it) = 0;
	virtual void remove(const_iterator it) = 0;

	virtual void pop() = 0;

	virtual bool empty() const = 0;
	virtual size_type size() const = 0;

	virtual reference top() = 0;

	virtual const_reference top() const = 0;

	virtual reference operator[](size_type ind) = 0;
	virtual const_reference operator[](size_type ind) const = 0;

	virtual iterator begin() = 0;
	virtual iterator end() = 0;

	virtual const_iterator begin() const = 0;
	virtual const_iterator end() const = 0;

	virtual const_iterator cbegin() const = 0;
	virtual const_iterator cend() const = 0;

	virtual std::unique_ptr<ordered_iterable> orderedIterable() = 0;
	virtual std::unique_ptr<const_ordered_iterable> orderedIterable() const = 0;
};

template<
	class T,
	class Container = std::vector<T>,
	class Compare = std::less<typename Container::value_type>,
	class SetIndex = DefaultSetIndex<typename Container::value_type>
>
class BinHeapForwarder: public BinHeapInterface<T> {
public:
	using heap_type = BinHeap<T, Container, Compare, SetIndex>;
	using heap_interface = BinHeapInterface<T>;

	using container_type = typename heap_type::container_type;
	using value_compare = typename heap_type::value_compare;
	using value_set_index = typename heap_type::value_set_index;

	using value_type = typename heap_interface::value_type;
	using size_type = typename heap_interface::size_type;
	using difference_type = typename heap_interface::difference_type;
	using reference = typename heap_interface::reference;
	using const_reference = typename heap_interface::const_reference;

	using iterator = typename heap_interface::iterator;
	using const_iterator = typename heap_interface::const_iterator;

	using ordered_iterator = typename heap_interface::ordered_iterator;
	using const_ordered_iterator = typename heap_interface::const_ordered_iterator;

	using ordered_iterable = typename heap_interface::ordered_iterable;
	using const_ordered_iterable = typename heap_interface::const_ordered_iterable;

	template<bool Const>
	class _OrderedIterator: public heap_interface::template _OrderedIterator<Const> {
	public:
		using iterator_type = typename std::conditional_t<Const, typename heap_type::const_ordered_iterator, typename heap_type::ordered_iterator>;
		using const_iterator_type = typename heap_type::const_ordered_iterator;

		using iterator_interface = std::conditional_t<Const, const_ordered_iterator, ordered_iterator>;
		using const_iterator_interface = const_ordered_iterator;

		using _iterator_forwarder = _OrderedIterator<Const>;
		using _const_iterator_forwarder = _OrderedIterator<true>;

		using iterator_category = typename iterator_type::iterator_category;
		using value_type = typename iterator_type::value_type;
		using difference_type = typename iterator_type::difference_type;
		using reference = typename iterator_type::reference;
		using pointer = typename iterator_type::pointer;

	protected:
		iterator_type iterator;

	public:
		_OrderedIterator(const iterator_type& iterator) : iterator(iterator) {}
		_OrderedIterator(iterator_type&& iterator) : iterator(std::move(iterator)) {}

		reference operator*() const override { return *iterator; }
		pointer operator->() const override { return iterator.operator->(); }
		iterator_interface& operator++() override {
			++iterator;
			return *this;
		}
		std::unique_ptr<iterator_interface> operator++(int) override { return std::make_unique<_iterator_forwarder>(iterator++); }
		bool operator==(const iterator_interface& other) const override { return iterator == dynamic_cast<const _iterator_forwarder&>(other).iterator; }
		bool operator!=(const iterator_interface& other) const override { return iterator != dynamic_cast<const _iterator_forwarder&>(other).iterator; }

		std::unique_ptr<iterator_interface> clone() const override { return std::make_unique<_iterator_forwarder>(iterator); }

		operator std::unique_ptr<const_iterator_interface>() const override { return std::make_unique<_const_iterator_forwarder>(const_iterator_type(iterator)); }
	};

	using _ordered_iterator_forwarder = _OrderedIterator<false>;
	using _const_ordered_iterator_forwarder  = _OrderedIterator<true>;

	template<bool Const>
	class _OrderedIterable: public heap_interface::template _OrderedIterable<Const> {
	public:
		using iterable_type = typename std::conditional_t<Const, typename heap_type::const_ordered_iterable, typename heap_type::ordered_iterable>;

		using iterator_interface = std::conditional_t<Const, const_ordered_iterator, ordered_iterator>;
		using const_iterator_interface = const_ordered_iterator;

		using _iterator_forwarder = std::conditional_t<Const, _const_ordered_iterator_forwarder, _ordered_iterator_forwarder>;
		using _const_iterator_forwarder = _const_ordered_iterator_forwarder;

	protected:
		iterable_type iterable;

	public:
		_OrderedIterable(const iterable_type& iterable) : iterable(iterable) {}
		_OrderedIterable(iterable_type&& iterable) : iterable(std::move(iterable)) {}

		std::unique_ptr<iterator_interface> begin() const override { return std::make_unique<_iterator_forwarder>(iterable.begin()); }
		std::unique_ptr<iterator_interface> end() const override { return std::make_unique<_iterator_forwarder>(iterable.end()); }
		std::unique_ptr<const_iterator_interface> cbegin() const override { return std::make_unique<_const_iterator_forwarder>(iterable.cbegin()); }
		std::unique_ptr<const_iterator_interface> cend() const override { return std::make_unique<_const_iterator_forwarder>(iterable.cend()); }
	};

	using _ordered_iterable_forwarder = _OrderedIterable<false>;
	using _const_ordered_iterable_forwarder  = _OrderedIterable<true>;

protected:
	heap_type heap;

public:
	template<class... Args>
	BinHeapForwarder(Args&&... args) : heap(std::forward<Args>(args)...) {}

	BinHeapForwarder(const heap_type& heap) : heap(heap) {}
	BinHeapForwarder(heap_type&& heap) : heap(std::move(heap)) {}

	void clear() override { heap.clear(); }

	void push(const value_type& value) override { heap.push(value); }
	void push(value_type&& value) override { heap.push(std::move(value)); }

	template<class... Args>
	void emplace(Args&&... args) { heap.emplace_back(std::forward<Args>(args)...); }

	void fix(size_type ind) override { heap.fix(ind); }
	void fix(iterator it) override { heap.fix(it); }
	void fix(const_iterator it) override { heap.fix(it); }

	void remove(size_type ind) override { heap.remove(ind); }
	void remove(iterator it) override { heap.remove(it); }
	void remove(const_iterator it) override { heap.remove(it); }

	void pop() override { heap.pop(); }

	bool empty() const override { return heap.empty(); }
	size_type size() const override { return heap.size(); }

	reference top() override { return heap.top(); }

	const_reference top() const override { return heap.top(); }

	reference operator[](size_type ind) override { return heap[ind]; }
	const_reference operator[](size_type ind) const override { return heap[ind]; }

	iterator begin() override { return heap.begin(); }
	iterator end() override { return heap.end(); }

	const_iterator begin() const override { return heap.begin(); }
	const_iterator end() const override { return heap.end(); }

	const_iterator cbegin() const override { return heap.cbegin(); }
	const_iterator cend() const override { return heap.cend(); }

	std::unique_ptr<ordered_iterable> orderedIterable() override { return std::make_unique<_ordered_iterable_forwarder>(heap.orderedIterable()); }
	std::unique_ptr<const_ordered_iterable> orderedIterable() const override { return std::make_unique<_const_ordered_iterable_forwarder>(heap.orderedIterable()); }
};

template<class T>
class AnyBinHeap {
public:
	using heap_interface = BinHeapInterface<T>;

private:
	std::unique_ptr<heap_interface> heapPtr;

public:
	using value_type = typename heap_interface::value_type;
	using size_type = typename heap_interface::size_type;
	using difference_type = typename heap_interface::difference_type;
	using reference = typename heap_interface::reference;
	using const_reference = typename heap_interface::const_reference;

	using iterator = typename heap_interface::iterator;
	using const_iterator = typename heap_interface::const_iterator;

	template<bool Const>
	class _OrderedIterator {
	public:
		using iterator_interface = typename std::conditional_t<Const, typename heap_interface::const_ordered_iterator, typename heap_interface::ordered_iterator>;
		using const_iterator_interface = typename heap_interface::const_ordered_iterator;

		using iterator_category = typename iterator_interface::iterator_category;
		using value_type = typename iterator_interface::value_type;
		using difference_type = typename iterator_interface::difference_type;
		using reference = typename iterator_interface::reference;
		using pointer = typename iterator_interface::pointer;

	protected:
		std::unique_ptr<iterator_interface> iteratorPtr;

	public:
		_OrderedIterator() = default;
		_OrderedIterator(std::unique_ptr<iterator_interface>&& iteratorPtr) : iteratorPtr(std::move(iteratorPtr)) {}

		_OrderedIterator(const _OrderedIterator<Const>& other) : iteratorPtr(other.iteratorPtr->clone()) {}
		_OrderedIterator(_OrderedIterator<Const>&& other) : iteratorPtr(std::move(other.iteratorPtr)) {}

		_OrderedIterator<Const>& operator=(const _OrderedIterator<Const>& other) {
			iteratorPtr = other.iteratorPtr->clone();
			return *this;
		}
		_OrderedIterator<Const>& operator=(_OrderedIterator<Const>&& other) {
			iteratorPtr = std::move(other.iteratorPtr);
			return *this;
		}

		~_OrderedIterator() = default;

		reference operator*() const { return *static_cast<const iterator_interface&>(*iteratorPtr); }
		pointer operator->() const { return static_cast<const iterator_interface&>(*iteratorPtr).operator->(); }
		_OrderedIterator<Const>& operator++() {
			++(*iteratorPtr);
			return *this;
		}
		_OrderedIterator<Const> operator++(int) { return _OrderedIterator<Const>((*iteratorPtr)++); }
		bool operator==(const _OrderedIterator<Const>& other) const { return static_cast<const iterator_interface&>(*iteratorPtr) == (*other.iteratorPtr); }
		bool operator!=(const _OrderedIterator<Const>& other) const { return static_cast<const iterator_interface&>(*iteratorPtr) != (*other.iteratorPtr); }

		operator _OrderedIterator<true>() const {
			// The conversion operator is virtually overloaded to allocate and return a copy of the iterator on the heap
			return _OrderedIterator<true>(std::unique_ptr<const_iterator_interface>(static_cast<const iterator_interface&>(*iteratorPtr)));
		}
	};

	using ordered_iterator = _OrderedIterator<false>;
	using const_ordered_iterator = _OrderedIterator<true>;

	template<bool Const>
	class _OrderedIterable {
	public:
		using iterable_interface = typename std::conditional_t<Const, typename heap_interface::const_ordered_iterable, typename heap_interface::ordered_iterable>;

		using iterator_type = typename std::conditional_t<Const, const_ordered_iterator, ordered_iterator>;
		using const_iterator_type = const_ordered_iterator;

	private:
		std::unique_ptr<iterable_interface> iterablePtr;

	public:
		_OrderedIterable() = default;
		_OrderedIterable(std::unique_ptr<iterable_interface>&& iterablePtr) : iterablePtr(std::move(iterablePtr)) {}

		iterator_type begin() const { return iterator_type(static_cast<const iterable_interface&>(*iterablePtr).begin()); }
		iterator_type end() const { return iterator_type(static_cast<const iterable_interface&>(*iterablePtr).end()); }
		const_iterator_type cbegin() const { return const_iterator_type(static_cast<const iterable_interface&>(*iterablePtr).cbegin()); }
		const_iterator_type cend() const { return const_iterator_type(static_cast<const iterable_interface&>(*iterablePtr).cend()); }
	};

	using ordered_iterable = _OrderedIterable<false>;
	using const_ordered_iterable = _OrderedIterable<true>;

	AnyBinHeap() = default;

	// template<class WrappedHeap>
	// AnyBinHeap(WrappedHeap&& h) : heapPtr(std::make_unique<WrappedHeap>(std::forward<WrappedHeap>(h))) {}

	template<class PureHeap>
	AnyBinHeap(PureHeap&& h) : heapPtr(std::make_unique<BinHeapForwarder<T, typename PureHeap::container_type, typename PureHeap::value_compare, typename PureHeap::value_set_index>>(std::forward<PureHeap>(h))) {}

	// template<class WrappedHeap>
	// AnyBinHeap& operator=(WrappedHeap&& h) {
	// 	heapPtr = std::make_unique<WrappedHeap>(std::forward<WrappedHeap>(h));
	// 	return *this;
	// }

	template<class PureHeap>
	AnyBinHeap& operator=(PureHeap&& h) {
		heapPtr = std::make_unique<BinHeapForwarder<T, typename PureHeap::container_type, typename PureHeap::value_compare, typename PureHeap::value_set_index>>(std::forward<PureHeap>(h));
		return *this;
	}

	void clear() { heapPtr->clear(); }

	void push(const value_type& value) { heapPtr->push(value); }
	void push(value_type&& value) { heapPtr->push(std::move(value)); }

	// template<class... Args>
	// void emplace(Args&&... args) { heapPtr->emplace_back(std::forward<Args>(args)...); }

	void fix(size_type ind) { heapPtr->fix(ind); }
	void fix(iterator it) { heapPtr->fix(it); }
	void fix(const_iterator it) { heapPtr->fix(it); }

	void remove(size_type ind) { heapPtr->remove(ind); }
	void remove(iterator it) { heapPtr->remove(it); }
	void remove(const_iterator it) { heapPtr->remove(it); }

	void pop() { heapPtr->pop(); }

	bool empty() const { return static_cast<const heap_interface&>(*heapPtr).empty(); }
	size_type size() const { return static_cast<const heap_interface&>(*heapPtr).size(); }

	reference top() { return heapPtr->top(); }

	const_reference top() const { return static_cast<const heap_interface&>(*heapPtr).top(); }

	reference operator[](size_type ind) { return (*heapPtr)[ind]; }
	const_reference operator[](size_type ind) const { return static_cast<const heap_interface&>(*heapPtr)[ind]; }

	iterator begin() { return heapPtr->begin(); }
	iterator end() { return heapPtr->end(); }

	const_iterator begin() const { return static_cast<const heap_interface&>(*heapPtr).begin(); }
	const_iterator end() const { return static_cast<const heap_interface&>(*heapPtr).end(); }

	const_iterator cbegin() const { return static_cast<const heap_interface&>(*heapPtr).cbegin(); }
	const_iterator cend() const { return static_cast<const heap_interface&>(*heapPtr).cend(); }

	ordered_iterable orderedIterable() { return ordered_iterable(heapPtr->orderedIterable()); }
	const_ordered_iterable orderedIterable() const { return const_ordered_iterable(static_cast<const heap_interface&>(*heapPtr).orderedIterable()); }
};

#endif
